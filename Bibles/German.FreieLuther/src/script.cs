using System;

// Epub.Links = false;

Epub.Page = book => {
    book = book+3;
    return $"ch{book:d3}.xhtml";
};
Program.Language = "german";

Console.WriteLine("Added epub rule.");
