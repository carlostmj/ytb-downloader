# YTB Downloader

Projeto modular para baixar musicas e videos com `yt-dlp`, suportando:

- linha de comando
- modo interativo dentro do terminal
- interface grafica
- Linux e Windows

Criado por **CarlosTMJ**.
GitHub: `https://github.com/carlostmj`

## Publicacao

Repositorio sugerido:

```text
https://github.com/carlostmj/ytb-downloader
```

## Projeto

- Autor: **CarlosTMJ**
- GitHub: `https://github.com/carlostmj`
- Changelog: [CHANGELOG.md](/home/carlos/Desktop/ytb-downloader/CHANGELOG.md)

## Requisitos

- Python 3.10+
- `ffmpeg` instalado no sistema
- `tkinter` instalado se quiser usar a GUI

No Ubuntu/Debian:

```bash
sudo apt install ffmpeg python3-tk
```

No Windows:

- instale Python com `tkinter` habilitado
- instale `ffmpeg` e deixe no `PATH`

## Instalacao

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Depois disso:

```bash
ytb-downloader
```

No Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -e .
ytb-downloader
```

## Uso rapido

Sem argumentos abre o modo interativo:

```bash
ytb-downloader
```

Baixar video MP4 para a pasta padrao:

```bash
ytb-downloader --mp4 --link "https://www.youtube.com/watch?v=VIDEO_ID"
```

Baixar usando apenas o ID do video:

```bash
ytb-downloader --mp3 --link "dgn0egjhDJs"
```

Baixar audio MP3 para outra pasta:

```bash
ytb-downloader --mp3 --link "https://www.youtube.com/watch?v=VIDEO_ID" --local "/caminho/de/saida"
```

Abrir o modo interativo no terminal:

```bash
ytb-downloader --interactive
```

Abrir a GUI:

```bash
ytb-downloader --gui
```

Baixar em lote a partir de um TXT:

```bash
ytb-downloader --mp3 --list "/caminho/links.txt"
```

Misturar um link direto com uma lista:

```bash
ytb-downloader --mp3 --link "dgn0egjhDJs" --list "/caminho/links.txt"
```

Escolher qualidade:

```bash
ytb-downloader --mp3 --link "dgn0egjhDJs" --audio-quality 192
ytb-downloader --mp4 --link "dgn0egjhDJs" --video-quality 720
```

Criar atalho de execucao rapida:

```bash
ytb-downloader --install-shortcut
```

No Linux isso cria:

- `~/.local/bin/ytb-downloader`
- `~/.local/share/applications/ytb-downloader.desktop`

No Windows o comando cria um launcher `.cmd` em `~/bin`.

## Diretorio padrao

Se `--local` nao for informado, o app salva em:

```text
<raiz-do-projeto>/downloads
```

## Arquivo TXT

```bash
ytb-downloader --mp3 --list "./links.txt"
```

Formato do arquivo:

```text
dgn0egjhDJs
https://www.youtube.com/watch?v=dgn0egjhDJs
# comentarios sao ignorados
```

Itens repetidos sao removidos automaticamente na fila da CLI e da GUI.

## GUI

A interface grafica agora permite:

- colar URL completa ou apenas o ID do video
- importar TXT com um item por linha
- remover duplicados da fila
- abrir a pasta de downloads
- parar a fila apos o item atual
- escolher qualidade de audio e video

## Publicar no GitHub

```bash
git init
git add .
git commit -m "feat: initial release"
git branch -M main
git remote add origin https://github.com/carlostmj/ytb-downloader.git
git push -u origin main
```

## Atualizar com changelog real

Para cada melhoria nova:

```bash
git checkout master
git pull
```

1. Atualize `CHANGELOG.md` em `Unreleased`.
2. Faça as mudancas no codigo.
3. Gere um commit claro, por exemplo:

```bash
git add .
git commit -m "feat: improve GUI queue workflow"
```

Quando quiser fechar uma versao:

1. Troque `Unreleased` por uma nova versao, por exemplo `0.2.0`.
2. Atualize a versao em `pyproject.toml`.
3. Crie uma tag:

```bash
git add .
git commit -m "chore: release 0.2.0"
git tag v0.2.0
git push origin master --tags
```

## Licenca

Este projeto usa a licenca MIT. Veja [LICENSE](/home/carlos/Desktop/ytb-downloader/LICENSE).
