from dbfread import DBF

DBF_PATH = "NOWE_PRG_Miejscowosci_POLSKA.dbf"

def main():
    table = DBF(
        DBF_PATH,
        encoding="utf-8",
        char_decode_errors="strict",
    )

    with open("city_names.txt", "w", encoding="utf-8") as out:
        for row in table:
            name = row["NAZWA_MSC"].strip()
            if name:
                out.write(name + "\n")

if __name__ == "__main__":
    main()
