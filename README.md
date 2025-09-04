# Biblia Libre

Biblia Libre is a collection of OpenSource & Public Domain Bibles. The Bibles use a specific version of Markdown, BibleMarkdown. Bible Markdown is normal Pandoc Markdown with the following extensions:

- For Footnotes you can make them more readable, by placing a marker ^label^ at the place of the footnote, but specifying the footnote later in the text with ordinary ^label^[Footnote] markdown. "label" must be a letter or word without any digits.
- You can have comments by bracing them with /\* and \*/ or by leading with // until the end of the line. /\* \*/ Comments can span multiple lines.
- Verse numbers are denoted with a @ character followed by a number, like this: @1 In the beginning was the Word and the Word was with God and the Word was God. @2 This was in the beginning...
- if the text contains the comment //!verse-paragraphs, each verse is rendered in a paragraph. For use in Psalms and Proverbs.
- Chapter numbers are denoted with a # markdown title and Chapter headings with a ## markdown title
- A special comment //!replace /regularexpression/replacement/regularexpression/replacement/... can be placed in the text. All the regular expressions will be replaced. You can choose another delimiter char than /, the first character encountered will be used as delimiter.

To edit the Markdown of the Bibles, you can use a normal editor like Typora, stackedit.io or VisualStudio Code.

The conversion from BibleMarkdown to other formats is done by a tool called bibmark. 
bibmark processes all the .md files in the current directory and converts them to other formats in the "out" subdirectory. The md files in the current directory must follow a naming schema, of two digits followed by a minus and the name of the bible book, e.g. like 01-Genesis.md or 02-Exodus.md. Bibmark only processes files with names adhering to that schema. The md files can be constructed from various source formats. For this, the source files must be placed in the subdirectory "src". In the "src" subdirectory you can place USFM files or zefania xml files, or a BibleEdit folder. You can also place a script.cs file in the "src" folder that will be executed when running bibmark, that can configure bibmark for certain tasks. Next you can place a file booknames.xml in the "src" subdirectory that contains names of Bible books in different languages. The names of the books should correspond to the titles of the books in the USFM files. Then you can also import a Parallel Verses file, linklist.xml, that contains parallel verses.

bibmark also creates a file called framework.md in the out folder that specifies chapter titles and paragraphs and footnotes. If you move this file to the src folder and it is newer than the Bible Markdown files, bibmark applies the chapter titles and paragraphs and footnotes found in the framework.md file to the Bible Markdown files.
In the framework.md file, the Bible Markdown files are specified by a # markdown title, the chapter numbers by a ## markdown title, and section titles by a ### markdown title.
Verses that contain a paragraph or a footnote are denoted with superscript markdown notation followed by a \ for a paragraph or a ^^ for a footnote marker, or a ^[Footnote]
footnote.

bibmark also creates a file verses.md in the out folder, a file that shows how many verses each chapter has, so you can compare different Bibles versifications.

You can also place a file linklist.xml in the src folder, to specify parallel verses included in footnotes, that will be imported and placed in the footnotes.

When importing framework.md or footnotes, one can map different versifications of the files to the current versification with placing the following files in src:
- parallelversesmap.md for mapping the verses of linklist.xml to the current versification.
- paragraphsmap.md for mapping the verses of paragraphs in framework.md to the current versification.
- titlesmap.md for mapping the verses of titles in framework.md to the current versification.
- footnotesmap.md for mapping of footnotes in framework.md to the current versification.
- duallanguagemap.md for mapping the versification of the secondary language to the primary language in two column two language bibles.


