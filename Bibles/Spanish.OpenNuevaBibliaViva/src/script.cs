using System;
using System.Text;
using System.Text.RegularExpressions;

// Epub.Links = false;
// Epub.OmitTitles = false;
// Epub.OmitFootnotes = false;
// Epub.CreateChapterLinks = false;
// Epub.TableOfContentsPage = "ch001.xhtml";

Epub.OmitParagraphs = false;
Epub.Page = book => {
    book = book+3;
    return $"ch{book:d3}.xhtml";
};
Program.Language = "spanish";
Program.Replace = "/SEÑOR/[Señor]{.smallcaps}";
// replace uppercase words with smallcaps
Program.Preprocess = txt => Regex.Replace(txt, @"[A-ZÑÓÍÉÁÚ][A-ZÑÓÍÉÁÚ]+", m => {

        if (Regex.IsMatch(m.Value, "^[IVXCDM]+$", RegexOptions.Singleline)) {
            // is roman number
            return m.Value;
        }
        var str = new StringBuilder("[");
        str.Append(m.Value[0]);
        for (int i = 1; i < m.Value.Length; i++) str.Append(Char.ToLower(m.Value[i]));
        str.Append("]{.smallcaps}");
        return str.ToString();
    });
Program.PreprocessImportUSFM = txt =>
{
    // Unify name of God
    //txt = txt.Replace(@"\nd Señor\nd*", "SEÑOR");
    // Remove titles
    txt = Regex.Replace(txt, @"\\s[0-9].*?(?:\r?\n|$)", "", RegexOptions.Singleline);
    txt = txt.Replace("―", "");
    return txt;
};


Program.EachVerseOnNewLine = true;

Program.Log("Added epub rule.");
