from __future__ import annotations

import threading
from pathlib import Path

from .config import WINDOW_TITLE, default_download_dir
from .downloader import download
from .models import DownloadRequest
from .utils import dedupe_entries, display_video_input, load_batch_entries, normalize_destination, normalize_video_input, open_in_file_manager


class DownloaderGUI:
    def __init__(self) -> None:
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry("980x690")
        self.root.minsize(860, 620)
        self.root.configure(bg="#f4efe6")

        self.queue: list[dict[str, str]] = []
        self.is_downloading = False
        self.stop_requested = False

        self.link_var = tk.StringVar()
        self.destination_var = tk.StringVar(value=str(default_download_dir()))
        self.media_var = tk.StringVar(value="mp3")
        self.audio_quality_var = tk.StringVar(value="128")
        self.video_quality_var = tk.StringVar(value="best")
        self.status_var = tk.StringVar(value="Pronto. Cole um link, um ID do video ou importe um TXT.")
        self.queue_count_var = tk.StringVar(value="Fila: 0 item")

        self._configure_styles()
        self._build()
        self._refresh_quality_state()

    def _configure_styles(self) -> None:
        style = self.ttk.Style()
        style.theme_use("clam")
        style.configure("Root.TFrame", background="#f4efe6")
        style.configure("Card.TFrame", background="#fffaf2", relief="flat")
        style.configure("Title.TLabel", background="#f4efe6", foreground="#1b1b18", font=("DejaVu Sans", 24, "bold"))
        style.configure("Subtitle.TLabel", background="#f4efe6", foreground="#665f57", font=("DejaVu Sans", 10))
        style.configure("Section.TLabel", background="#fffaf2", foreground="#1e3a34", font=("DejaVu Sans", 11, "bold"))
        style.configure("Body.TLabel", background="#fffaf2", foreground="#3f3c37", font=("DejaVu Sans", 10))
        style.configure("Accent.TButton", font=("DejaVu Sans", 10, "bold"))
        style.configure("Queue.Treeview", rowheight=28, font=("DejaVu Sans Mono", 10))
        style.configure("Queue.Treeview.Heading", font=("DejaVu Sans", 10, "bold"))

    def _build(self) -> None:
        header = self.ttk.Frame(self.root, style="Root.TFrame", padding=(24, 22, 24, 10))
        header.pack(fill="x")
        self.ttk.Label(header, text="YTB Downloader", style="Title.TLabel").pack(anchor="w")
        self.ttk.Label(
            header,
            text="Cole a URL inteira, apenas o ID depois de v=, ou importe um TXT com um item por linha.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        content = self.ttk.Frame(self.root, style="Root.TFrame", padding=(24, 0, 24, 24))
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=5)
        content.columnconfigure(1, weight=4)
        content.rowconfigure(0, weight=1)

        left_card = self.ttk.Frame(content, style="Card.TFrame", padding=20)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right_card = self.ttk.Frame(content, style="Card.TFrame", padding=20)
        right_card.grid(row=0, column=1, sticky="nsew")

        self._build_form(left_card)
        self._build_queue(right_card)

    def _build_form(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        self.ttk.Label(parent, text="Entrada rapida", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.ttk.Label(
            parent,
            text="Aceita link completo ou apenas o codigo do video com 11 caracteres.",
            style="Body.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 12))

        entry = self.ttk.Entry(parent, textvariable=self.link_var, font=("DejaVu Sans Mono", 11))
        entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        entry.focus_set()

        format_box = self.ttk.Frame(parent, style="Card.TFrame")
        format_box.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 12))
        self.ttk.Radiobutton(format_box, text="MP3", value="mp3", variable=self.media_var, command=self._refresh_quality_state).pack(side="left")
        self.ttk.Radiobutton(format_box, text="MP4", value="mp4", variable=self.media_var, command=self._refresh_quality_state).pack(side="left", padx=(10, 0))

        self.ttk.Label(parent, text="Qualidade MP3", style="Section.TLabel").grid(row=4, column=0, sticky="w")
        self.audio_quality_box = self.ttk.Combobox(
            parent,
            textvariable=self.audio_quality_var,
            values=("128", "192", "256", "320"),
            state="readonly",
        )
        self.audio_quality_box.grid(row=5, column=0, sticky="ew", pady=(4, 14), padx=(0, 10))

        self.ttk.Label(parent, text="Qualidade MP4", style="Section.TLabel").grid(row=4, column=1, sticky="w")
        self.video_quality_box = self.ttk.Combobox(
            parent,
            textvariable=self.video_quality_var,
            values=("best", "1080", "720", "480", "360"),
            state="readonly",
        )
        self.video_quality_box.grid(row=5, column=1, sticky="ew", pady=(4, 14))

        self.ttk.Label(parent, text="Pasta de destino", style="Section.TLabel").grid(row=6, column=0, sticky="w")
        destination_row = self.ttk.Frame(parent, style="Card.TFrame")
        destination_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(4, 14))
        destination_row.columnconfigure(0, weight=1)
        self.ttk.Entry(destination_row, textvariable=self.destination_var).grid(row=0, column=0, sticky="ew")
        self.ttk.Button(destination_row, text="Escolher pasta", command=self._choose_directory).grid(row=0, column=1, padx=(10, 0))

        actions = self.ttk.Frame(parent, style="Card.TFrame")
        actions.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(4, 16))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        actions.columnconfigure(2, weight=1)
        self.add_button = self.ttk.Button(actions, text="Adicionar a fila", style="Accent.TButton", command=self._add_current_entry)
        self.add_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.import_button = self.ttk.Button(actions, text="Importar TXT", command=self._import_txt)
        self.import_button.grid(row=0, column=1, sticky="ew", padx=4)
        self.download_button = self.ttk.Button(actions, text="Baixar agora", command=self._start_queue)
        self.download_button.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        utility_actions = self.ttk.Frame(parent, style="Card.TFrame")
        utility_actions.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        utility_actions.columnconfigure(0, weight=1)
        utility_actions.columnconfigure(1, weight=1)
        self.open_folder_button = self.ttk.Button(utility_actions, text="Abrir downloads", command=self._open_downloads_folder)
        self.open_folder_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.stop_button = self.ttk.Button(utility_actions, text="Parar apos atual", command=self._request_stop)
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.stop_button.state(["disabled"])

        progress = self.ttk.Frame(parent, style="Card.TFrame")
        progress.grid(row=11, column=0, columnspan=2, sticky="ew")
        progress.columnconfigure(0, weight=1)
        self.progress_bar = self.ttk.Progressbar(progress, mode="indeterminate")
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        self.ttk.Label(progress, textvariable=self.status_var, style="Body.TLabel", wraplength=470).grid(row=1, column=0, sticky="w", pady=(10, 0))

    def _build_queue(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        self.ttk.Label(parent, text="Fila de downloads", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.ttk.Label(parent, textvariable=self.queue_count_var, style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 12))

        columns = ("input", "format", "quality", "status")
        self.queue_tree = self.ttk.Treeview(parent, columns=columns, show="headings", style="Queue.Treeview")
        self.queue_tree.heading("input", text="Video / ID")
        self.queue_tree.heading("format", text="Formato")
        self.queue_tree.heading("quality", text="Qualidade")
        self.queue_tree.heading("status", text="Status")
        self.queue_tree.column("input", width=240, anchor="w")
        self.queue_tree.column("format", width=65, anchor="center")
        self.queue_tree.column("quality", width=80, anchor="center")
        self.queue_tree.column("status", width=110, anchor="center")
        self.queue_tree.grid(row=2, column=0, sticky="nsew")

        scrollbar = self.ttk.Scrollbar(parent, orient="vertical", command=self.queue_tree.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.queue_tree.configure(yscrollcommand=scrollbar.set)

        queue_actions = self.ttk.Frame(parent, style="Card.TFrame")
        queue_actions.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        queue_actions.columnconfigure(0, weight=1)
        queue_actions.columnconfigure(1, weight=1)
        self.remove_button = self.ttk.Button(queue_actions, text="Remover selecionado", command=self._remove_selected)
        self.remove_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.clear_button = self.ttk.Button(queue_actions, text="Limpar fila", command=self._clear_queue)
        self.clear_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _refresh_quality_state(self) -> None:
        is_audio = self.media_var.get() == "mp3"
        self.audio_quality_box.state(["!disabled"] if is_audio else ["disabled"])
        self.video_quality_box.state(["disabled"] if is_audio else ["!disabled"])

    def _choose_directory(self) -> None:
        from tkinter import filedialog

        selected = filedialog.askdirectory(initialdir=self.destination_var.get() or str(default_download_dir()))
        if selected:
            self.destination_var.set(selected)

    def _add_current_entry(self) -> None:
        from tkinter import messagebox

        raw_value = self.link_var.get().strip()
        normalized = normalize_video_input(raw_value)
        if not normalized:
            messagebox.showerror(WINDOW_TITLE, "Cole um link ou informe o ID do video para adicionar na fila.")
            return

        quality = self.audio_quality_var.get() if self.media_var.get() == "mp3" else self.video_quality_var.get()
        if not self._append_queue_item(normalized, raw_value, self.media_var.get(), quality):
            messagebox.showinfo(WINDOW_TITLE, "Esse item ja esta na fila.")
            return
        self.link_var.set("")
        self._update_queue_count()
        self.status_var.set("Item adicionado a fila.")

    def _import_txt(self) -> None:
        from tkinter import filedialog, messagebox

        path = filedialog.askopenfilename(
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if not path:
            return

        entries = dedupe_entries(load_batch_entries(path))
        if not entries:
            messagebox.showerror(WINDOW_TITLE, "Nenhum link ou ID valido foi encontrado no TXT.")
            return

        quality = self.audio_quality_var.get() if self.media_var.get() == "mp3" else self.video_quality_var.get()
        added_count = 0
        for entry in entries:
            if self._append_queue_item(entry, display_video_input(entry), self.media_var.get(), quality):
                added_count += 1

        self._update_queue_count()
        self.status_var.set(f"TXT importado: {added_count} item(ns) adicionados.")

    def _remove_selected(self) -> None:
        selected = self.queue_tree.selection()
        if not selected:
            return
        indexes = sorted((self.queue_tree.index(item_id), item_id) for item_id in selected)
        for index, item_id in reversed(indexes):
            self.queue_tree.delete(item_id)
            del self.queue[index]
        self._update_queue_count()
        self.status_var.set("Item(ns) removido(s) da fila.")

    def _clear_queue(self) -> None:
        self.queue.clear()
        for item_id in self.queue_tree.get_children():
            self.queue_tree.delete(item_id)
        self._update_queue_count()
        self.status_var.set("Fila limpa.")

    def _start_queue(self) -> None:
        from tkinter import messagebox

        if self.is_downloading:
            messagebox.showinfo(WINDOW_TITLE, "Ja existe uma fila sendo processada.")
            return

        if not self.queue and self.link_var.get().strip():
            self._add_current_entry()

        if not self.queue:
            messagebox.showerror(WINDOW_TITLE, "Adicione pelo menos um item na fila antes de baixar.")
            return

        self.is_downloading = True
        self.stop_requested = False
        self._set_controls_enabled(False)
        self.progress_bar.start(9)
        self.status_var.set("Fila iniciada...")
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _process_queue(self) -> None:
        destination = normalize_destination(self.destination_var.get().strip() or None, default_download_dir())
        results: list[str] = []
        queue_snapshot = list(self.queue)

        for index, item in enumerate(queue_snapshot):
            if self.stop_requested:
                results.append("Parado")
                self._set_row_status(index, "Parado")
                continue
            self._set_row_status(index, "Baixando")
            self._set_status(f"Baixando {index + 1}/{len(self.queue)}: {item['display']}")

            request = DownloadRequest(
                link=item["source"],
                destination=destination,
                audio_only=item["format"] == "mp3",
                video_only=item["format"] == "mp4",
                audio_bitrate=item["quality"] if item["format"] == "mp3" else self.audio_quality_var.get(),
                video_quality=item["quality"] if item["format"] == "mp4" else self.video_quality_var.get(),
            )
            result = download(request, callback=self._set_status)
            final_status = "Concluido" if result.success else "Erro"
            self._set_row_status(index, final_status)
            results.append(final_status)
            if self.stop_requested:
                for remaining_index in range(index + 1, len(queue_snapshot)):
                    self._set_row_status(remaining_index, "Parado")
                    results.append("Parado")
                break

        success_count = sum(1 for item in results if item == "Concluido")
        self.root.after(0, self.progress_bar.stop)
        self.root.after(0, lambda: self._finish_queue(success_count, len(queue_snapshot), results))

    def _finish_queue(self, success_count: int, total: int, results: list[str]) -> None:
        from tkinter import messagebox

        self.is_downloading = False
        self.stop_requested = False
        self._set_controls_enabled(True)
        stopped_count = sum(1 for item in results if item == "Parado")
        self.status_var.set(f"Fila finalizada: {success_count}/{total} concluido(s), {stopped_count} parado(s).")
        messagebox.showinfo(
            WINDOW_TITLE,
            f"Fila finalizada: {success_count}/{total} download(s) concluido(s), {stopped_count} parado(s).",
        )

    def _set_status(self, message: str) -> None:
        self.root.after(0, lambda: self.status_var.set(message))

    def _set_row_status(self, index: int, status: str) -> None:
        def update_row() -> None:
            children = self.queue_tree.get_children()
            if index >= len(children):
                return
            values = list(self.queue_tree.item(children[index], "values"))
            values[3] = status
            self.queue_tree.item(children[index], values=values)
            self.queue[index]["status"] = status

        self.root.after(0, update_row)

    def _update_queue_count(self) -> None:
        total = len(self.queue)
        label = "item" if total == 1 else "itens"
        self.queue_count_var.set(f"Fila: {total} {label}")

    def _append_queue_item(self, source: str, display: str, media_format: str, quality: str) -> bool:
        for existing_item in self.queue:
            if existing_item["source"] == source and existing_item["format"] == media_format and existing_item["quality"] == quality:
                return False
        self.queue.append(
            {
                "source": source,
                "display": display_video_input(display),
                "format": media_format,
                "quality": quality,
                "status": "Na fila",
            }
        )
        self.queue_tree.insert("", "end", values=(display_video_input(display), media_format.upper(), quality, "Na fila"))
        return True

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = ["!disabled"] if enabled else ["disabled"]
        stop_state = ["disabled"] if enabled else ["!disabled"]
        for widget in (
            self.add_button,
            self.import_button,
            self.download_button,
            self.remove_button,
            self.clear_button,
            self.open_folder_button,
        ):
            widget.state(state)
        self.stop_button.state(stop_state)

    def _open_downloads_folder(self) -> None:
        from tkinter import messagebox

        destination = normalize_destination(self.destination_var.get().strip() or None, default_download_dir())
        if not open_in_file_manager(destination):
            messagebox.showerror(WINDOW_TITLE, "Nao foi possivel abrir a pasta de downloads neste sistema.")

    def _request_stop(self) -> None:
        self.stop_requested = True
        self.status_var.set("Parada solicitada. A fila sera encerrada apos o item atual.")

    def run(self) -> None:
        self.root.mainloop()


def run_gui() -> int:
    try:
        app = DownloaderGUI()
        app.run()
        return 0
    except ModuleNotFoundError as exc:
        print(f"GUI indisponivel neste sistema: {exc}")
        return 1
