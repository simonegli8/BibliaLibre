# Biblia Libre

Biblia Libre is a collection of OpenSource & Public Domain Bibles. The Bibles use a specific version of Markdown, BibleMarkdown. Bible Markdown is normal Pandoc Markdown with the following extensions:

Bible Markdown is normal pandoc Markdown with the following extensions:

- For Footnotes you can make them more readable, by placing a marker ^label^ at the place of the footnote, but specifying the footnote later in the text with ordinary ^label^[Footnote] markdown. "label" must be a letter or word without any digits.
- You can have comments by bracing them with /\* and \*/ or by leading with // until the end of the line. /\* \*/ Comments can span multiple lines.
- Verse numbers are denoted with a @ character followed by a number, like this: @1 In the beginning was the Word and the Word was with God and the Word was God. @2 This was in the beginning...
- if the text contains the comment //!verse-paragraphs, each verse is rendered in a paragraph. For use in Psalms and Proverbs.
- Chapter numbers are denoted with a # markdown title and Chapter headings with a ## markdown title
- A special comment //!replace /regularexpression/replacement/regularexpression/replacement/... can be placed in the text. All the regular expressions will be replaced. You can choose another delimiter char than /, the first character encountered will be used as delimiter.

# Installing BibleMarkdown

You can install bibmark on Windows, Linux and MacOS. You need to have [.NET 10 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/10.0) installed. Then you can execute the following command in a shell:

```
dotnet tool install -g BibleMarkdown
```

After this, bibmark is added to your PATH and you can execute it from any folder:

```
bibmark
```

To show a help page execute `bibmark -?`.

Alernatively, on Windows, you can also install BibleMarkdown with the MSI Installer.

# Usage of bibmark

In order to use bibmark, you need to place your Bible in a folder of the filesystem. You then place the source files you want to initially create your BibleMarkdown files from in a subfolder src. You can place USFM files, a Zefania XML file, a BibleEdit folder or a folder `bibmark` containing BibleMarkdown in the src folder. Then, when you run `bibmark -s` inside that folder, bibmark will scan the src folder for sources and create BibleMarkdown *.md files in the main folder. It will then further process those *.md files to the out folder. It will create Pandoc Markdown files in out/pandoc, LaTeX files in out/tex, HTML files in out/html and USFM files in out/usfm. If you ommit the `-s` argument from `bibmark`, bibmark will omit scanning the src folder, and only process the BibleMarkdown files present in the main folder. In order for bibmark to process the md files, they must be specially named, starting with digits/period, followed by a '-' dash and the name of the file.

bibmark also creates a file called outline.md & outline.xml in the out folder that specifies chapter titles, paragraphs and footnotes. If you move this file to the src folder and it is newer than the Bible Markdown files, bibmark applies the chapter titles and paragraphs and footnotes found in the outline.md or outline.xml file to the Bible Markdown files.
In the outline.md file, the Bible Markdown files are specified by a # markdown title, the chapter numbers by a ## markdown title, and chapter titles by a ### markdown title.
Verses that end with a paragraph or a footnote are denoted with @n with n denoting the verse number, followed by a \ for a paragraph or a ^^ for a footnote marker, or a ^[Footnote]
footnote.
You can also specify mutliple *.outline.md files, that will be merged.
If you put a //!append directive in one of those files, The titles, paragraphs and footnotes will be added to the .md files. If you ommit //!append, the titles, paragraphs and footnotes in the outline.md files will replace the titles, paragraphs and footnotes in the .md files.
You can also put the .outline.md files in the folder with your .md files, in that case the outlines will be applied to the .md files on output generation.
You can also change the versification of the .outline.md files by putting a //!map *&lt;versification&gt;* directive in the .outline.md file or a Map attribute on the BibleFramework root node in outline.xml.
You then put a verse mapping in the file versification.map.md.
The syntax of the verse mapping md file is as follows:

```
# <book>
<chapter>:<verse>=><tochapter>:<toverse> <chapter2>:<verse2>=><tochapter2>:<toverse2> ...

# <book2>
...
```

For example the following

```
# Números
12:16=>13:1 13:1=>13:2 13:33=>13:33
```

will point 12:16 to 13:1 and then all verses one up, until verse 13:33.
You can create the mapping files by comparing the verseinfo.md (see below) files of the different bibles via the diff tool.

bibmark also creates a file verseinfo.md in the out folder, a file that shows how many verses each chapter has, so you can compare different Bibles versifications.

You can also place a file linklist.xml in the src folder, to specify parallel verses included in footnotes, that will be imported and placed in the footnotes. This file will be exported as ParallelVerses.outline.md & ParallelVerses.outline.xml in the main directory.

For examples of the various input files like booknames.xml, linklist.xml, outline.md etc. you can have a look at the Bibles in the BibliaLibre project at
https://github.com/biblia-del-pueblo/BibliaLibre.
