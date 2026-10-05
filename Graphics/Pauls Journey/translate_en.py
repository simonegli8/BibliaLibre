"""Translate the Spanish map SVG to English by replacing text nodes only (keeps any manual edits).

  python translate_en.py viajes-de-pablo-completo.svg pauls-journey-full.svg
"""
import re, sys

EN = {
    "Mar Mediterráneo": "Mediterranean Sea", "Mar Egeo": "Aegean Sea", "Mar Jónico": "Ionian Sea",
    "Mar Adriático": "Adriatic Sea", "Mar Tirreno": "Tyrrhenian Sea", "Mar Negro": "Black Sea",
    "ITALIA": "ITALY", "GRECIA": "GREECE", "SIRIA": "SYRIA", "CHIPRE": "CYPRUS", "CRETA": "CRETE",
    "EGIPTO": "EGYPT", "LIBIA": "LIBYA", "SICILIA": "SICILY",
    "Jerusalén": "Jerusalem", "Cesarea": "Caesarea", "Tolemaida": "Ptolemais", "Tiro": "Tyre", "Sidón": "Sidon",
    "Damasco": "Damascus", "Antioquía": "Antioch", "Tarso": "Tarsus", "Salamina": "Salamis", "Pafos": "Paphos",
    "Perge": "Perga", "Antioquía de Pisidia": "Pisidian Antioch", "Iconio": "Iconium", "Listra": "Lystra",
    "Asos": "Assos", "Éfeso": "Ephesus", "Mileto": "Miletus", "Rodas": "Rhodes", "Mira": "Myra",
    "Cnido": "Cnidus", "Buenos Puertos": "Fair Havens", "Siracusa": "Syracuse", "Regio": "Rhegium",
    "Roma": "Rome", "Filipos": "Philippi", "Tesalónica": "Thessalonica", "Atenas": "Athens", "Corinto": "Corinth",
    "Los viajes del apóstol Pablo": "The Journeys of the Apostle Paul",
    "Hechos de los Apóstoles, c. 34 – 60 d. C.": "Acts of the Apostles, c. AD 34 – 60",
    "Leyenda": "Legend",
    "Primer viaje (c. 46–48 d. C.)": "First journey (c. AD 46–48)",
    "Segundo viaje (c. 49–52 d. C.)": "Second journey (c. AD 49–52)",
    "Tercer viaje (c. 53–57 d. C.)": "Third journey (c. AD 53–57)",
    "Viaje a Roma (c. 59–60 d. C.)": "Voyage to Rome (c. AD 59–60)",
    "Camino de Damasco (c. 34 d. C.)": "Road to Damascus (c. AD 34)",
    "Por mar": "By sea", "Por tierra": "By land", "Ciudad visitada": "City visited",
    "Centro principal": "Major centre",
    # same in both languages: Seleucia, Derbe, Troas, Mitylene, Cos, Patara, Malta, Puteoli, Berea, JUDEA, ASIA MINOR
}

src, dst = sys.argv[1:3]
s = open(src, encoding="utf-8").read()
missing = set()


def sub(m):
    t = m.group(1)
    key = t.strip()
    if key in EN:
        return ">" + t.replace(key, EN[key]) + "<"
    if key and key not in {"Seleucia", "Derbe", "Troas", "Mitylene", "Cos", "Patara", "Malta", "Puteoli",
                           "Berea", "JUDEA", "ASIA MINOR"} and not key.startswith(("data:", "{")):
        missing.add(key)
    return m.group(0)


out = re.sub(r">([^<>]+)<", sub, s)
open(dst, "w", encoding="utf-8").write(out)
print("untranslated text nodes:", sorted(missing) or "none")
