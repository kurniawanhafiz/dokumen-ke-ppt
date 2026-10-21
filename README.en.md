# dokumen-ke-ppt

English | [Bahasa Indonesia](README.md)

A skill that turns academic documents (papers, assignments, case studies, reports) into Indonesian-language presentation slides. The source can be .docx, .pdf, .md, or plain text. The output is two files: a PPT with Morph transitions and APA citations, and a .docx with speaker notes.

Current version: v1. This skill continues `makalah-ke-ppt` (v1 to v3) and was renamed because its sources are no longer limited to papers. Note that the slides and speaker notes it produces are in Indonesian only.

## Contents

- [Output](#output)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Repository layout](#repository-layout)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Author](#author)
- [License](#license)

## Output

- `PPT-[short title].pptx`: an opening slide, one content slide per sub-topic, and a closing "Terima Kasih" (Thank You) slide. Every slide has 3 to 5 sentences of speaker notes.
- `Speaker-Notes-[short title].docx`: the notes for all slides in one document (Times New Roman 12).

## How it works

1. The skill reads the source and extracts the identity details: title, group, members, course, lecturer. Missing details are asked for, never invented.
2. Anything still unknown (color, slide count, structure for non-paper sources) is asked in a single round of questions.
3. A slide plan is written first: the title and sub-topics covered by each slide.
4. Slides are built with the chosen palette, Poppins and Lato fonts, icons, and decorative elements that repeat on every slide so Morph animates smoothly. Images, tables, formulas, and Arabic text are handled according to their type.
5. Speaker notes are written per slide and collected into the .docx file.
6. Morph transitions are added, the PPT is validated, and every slide is rendered to an image and checked for clipped text, overlapping elements, stretched images, and fidelity to the source.

## Requirements

This skill is meant to run in Claude (Anthropic) with skills support. The environment it runs in needs:

- The built-in `pptx` and `docx` skills (used to validate the PPT and build the notes document).
- Python 3 with `matplotlib` and `Pillow` (for `render_rumus.py` and image cropping).
- Node.js with `pptxgenjs`, `react`, `react-dom`, `react-icons`, and `sharp` (for building slides and icons).
- LibreOffice and `pdftoppm` (for rendering slides to images during checks).
- The Poppins, Lato, and Amiri fonts (Amiri is only for Arabic text) on the computer that opens the PPT.
- PowerPoint 2019 or 365 to see Morph transitions.

## Installation

This repository is the skill folder itself: `SKILL.md` sits at the repository root.

**With git** (example for Claude Code; replace `kurniawanhafiz` with the GitHub account that owns the repository):

```
git clone https://github.com/kurniawanhafiz/dokumen-ke-ppt.git ~/.claude/skills/dokumen-ke-ppt
```

**With a ZIP:** download the ZIP from GitHub, extract it, and rename the folder to `dokumen-ke-ppt` (the folder name must match the skill name). Copy it to the skills location used by your environment. For the Claude app, upload the ZIP through the skills settings, following Anthropic's official instructions.

Make sure the `scripts/` folder is copied too, because `SKILL.md` calls the scripts inside it. If you still have the old `makalah-ke-ppt` skill, remove it so the two do not compete.

## Usage

Invoke the skill with `/dokumen-ke-ppt`, or simply ask for a presentation from your document. Put flags in the prompt, or ask for the same thing in plain words ("make it purple", "10 slides only").

### Flags

| Flag | What it does |
|---|---|
| `--hijau` | Dark green + cream palette |
| `--navy` | Navy + cream palette |
| `--marun` | Maroon + cream palette |
| `--teal` | Dark teal + cream palette |
| `--cokelat` | Dark brown + cream palette |
| `--hitam` | Black + cream palette, title line in gold |
| `--warna=<hex or name>` | Your own color, e.g. `--warna=#7A1F5C` or `--warna=ungu` |
| `--bagi` | Speaker notes list the speaker per member and the duration of each slide |
| `--pustaka` | Adds a References slide before the closing slide |
| `--slide=N` | Exactly N slides in total |

If no color flag is given, the skill asks which color you want. A custom color that is too light is darkened automatically so the text stays readable, and the skill says so in its reply.

### Example prompts

A regular paper:

```
/dokumen-ke-ppt buatkan PPT dari makalah terlampir --navy
```

A non-paper assignment (case study, report). The skill offers a slide structure first because the source has no chapters:

```
/dokumen-ke-ppt buatkan PPT dari tugas studi kasus BPMN terlampir --hijau --slide=10
```

A group presentation with speaker assignment. Each slide gets a line `Pembicara: [Name] | Durasi: ±N menit`, and the notes .docx includes a summary table of the assignments:

```
/dokumen-ke-ppt buatkan PPT dari makalah terlampir --marun --bagi, total durasi 15 menit
```

A custom color:

```
/dokumen-ke-ppt buatkan PPT dari makalah terlampir --warna=#7A1F5C
```

## Repository layout

```
dokumen-ke-ppt/
├── SKILL.md            Full instructions read by Claude
├── README.md           Documentation (Indonesian)
├── README.en.md        Documentation (English)
├── LICENSE             MIT license
├── .gitignore
└── scripts/
    ├── palette.py
    ├── add_morph.py
    ├── make_icons.mjs
    └── render_rumus.py
```

### scripts/

The skill calls these scripts automatically. This section is for running them by hand, from the repository root.

**palette.py** turns a color flag into a palette (JSON) and checks the contrast against the cream background.

```
python3 scripts/palette.py --hijau
python3 scripts/palette.py "--warna=#7A1F5C"
```

**add_morph.py** adds a Morph transition to every slide of a .pptx. It is safe to run again, and the output file must differ from the input file.

```
python3 scripts/add_morph.py PPT-mentah.pptx PPT-final.pptx
```

**make_icons.mjs** renders react-icons icons into transparent, colored 256 px PNGs. Modules are looked up in the working folder first, then in the global npm folder.

```
node scripts/make_icons.mjs --color 1B2A4A --out ikon FaBook MdSchool
```

**render_rumus.py** renders math formulas (matplotlib mathtext syntax, a subset of LaTeX) into transparent PNGs.

```
python3 scripts/render_rumus.py --color 1B2A4A --size 32 --out rumus1.png "\binom{n}{k}=\frac{n!}{k!(n-k)!}"
```

## Known limitations

- **Morph:** only shown in PowerPoint 2019 and 365. Other apps fall back to a fade. LibreOffice previews do not show Morph either, so the motion can only be checked in PowerPoint itself.
- **Fonts:** Poppins, Lato, and Amiri must be installed on the computer that opens the PPT. Otherwise PowerPoint substitutes fonts and the layout may shift. The skill can be asked to use Calibri instead.
- **Language:** slides and notes are in Indonesian only.
- **Formulas:** rendered as images, so they cannot be edited in PowerPoint. One-line formulas without fractions or roots are written as plain text.
- **Palette:** content slides always use a cream background (#F5EFE0). Only the main color changes. The layout is fixed as well, with no alternative themes.
- **Network:** installing npm packages needs access to the registry. Where that is not available, the packages must already be installed.
- **Unattended sessions:** if the skill runs without being able to ask questions, it uses `--navy` and the default slide-count rules, and says so in its reply.
- **Accuracy:** the skill keeps numbers, definitions, names, and verses identical to the source, but double-check before presenting.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Fonts look wrong or different | Fonts are not installed | Install Poppins, Lato, and Amiri from Google Fonts, or ask the skill to use Calibri |
| Transition does not animate | Not PowerPoint 2019/365 | Open in PowerPoint and check the Transitions tab: it should say Morph |
| `File keluaran harus beda dari file masukan.` | `add_morph.py` input and output names are the same | Give the output a different name |
| `Paket belum terpasang.` from `make_icons.mjs` | `react`, `react-dom`, or `sharp` not found | Run `npm install react react-dom react-icons sharp` in the working folder, or check `ls $(npm root -g)` |
| `npm install` fails with `ENOTFOUND registry.npmjs.org` | The npm registry is unreachable from this network | Use globally installed packages, or install from another network |
| `Gagal NamaIkon: ikon tidak ada di paket` | Wrong icon name or prefix | Check the icon name in the react-icons documentation (prefixes like `Fa`, `Md`, `Io5`) |
| `require('pptxgenjs')` fails | Node cannot find the global package | Run with `NODE_PATH=$(npm root -g) node ...` |
| `render_rumus.py` raises a mathtext error | Unsupported LaTeX command | Simplify the formula; `\frac`, `\binom`, `\sqrt`, superscripts, and subscripts are supported |
| `Warna '...' tidak dikenali.` | Color name is not in the list | Use hex: `--warna=#RRGGBB` |
| Result is darker than the requested color | Contrast against cream is below 4.5 | This is intentional so the text stays readable; pick a darker color yourself for an exact match |

## Author

Created by **Kurniawan Hafiz**.

## License

Released under the [MIT license](LICENSE).
