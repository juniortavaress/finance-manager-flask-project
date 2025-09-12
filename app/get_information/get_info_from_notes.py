import os 
import fitz  # PyMuPDF
import re
import pandas as pd 
import traceback

class GetNotesInfo:
    def __init__(self):
        pdf_paths = GetNotesInfo.find_pdfs()

        ignored_files = {
            r'notes\2022\11.22\5936158.pdf',
            r'notes\2022\12.22\6247246.pdf',
            r'notes\2023\01.23\52263187.pdf',
            r'notes\2023\08.23\9015035.pdf',
            r'notes\2023\10.23\9495200.pdf',
            r'notes\2024\01.24\10706060.pdf',
            r'notes\2024\06.24\12134759.pdf',
            r'notes\2024\10.24\14440636.pdf',
            r'notes\2024\11.24\14627938.pdf'
        }

        # ignored_files = {}

        all_dfs = []
        for file in pdf_paths:
            if file not in ignored_files:
                df = GetNotesInfo.read_pdf(file)
                if df is not None:
                    all_dfs.append(df)

        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            print(final_df)
        else:
            print("No data extracted.")


    @staticmethod
    def find_pdfs(path = 'notes'):
        pdf_paths = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    pdf_paths.append(full_path)
        return pdf_paths
            

    @staticmethod
    def read_pdf(file):
        """
        Reads a PDF note file, extracts tabular trade data, calculates proportional fees,
        and returns a DataFrame with adjusted final values.
        """
        try:
            with fitz.open(file) as doc:
                text = "".join(page.get_text() for page in doc)

                # for page in doc:
                #     text += page.get_text()
                
                date = re.search(r'(Data Preg[aã]o)\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE).group(2)
                total_price = re.search(r'L[ií]quido para.*?(-?[\d\.]+,\d{2})', text, re.IGNORECASE | re.DOTALL).group(1)
                negotiation_number = re.search(r'Número da nota\s*\n\s*(\d+)', text, re.IGNORECASE).group(1)

            OBS_CODES = {"#", "F", "B", "A", "H", "X", "P", "Y", "L", "T", "I", "@", '@#'}
            HEADER = ["Market", "B/S", "Market Type", "Ticker", "Quantity", "Unit Price", "Value Without Fee", "D/C"]
            start_idx = text.find("Valor/Ajuste D/C")
            end_idx = text.find("Resumo dos Negócios")
            lines = text[start_idx:end_idx].strip().splitlines()[1:]
            cleaned_lines = [line for line in lines if line.strip() not in OBS_CODES]
            records = [cleaned_lines[i:i+8] for i in range(0, len(cleaned_lines), 8)]

            # Create DataFrame and clean structure
            df = pd.DataFrame(records, columns=HEADER)
            df["Data"] = date
            df["Negotiation Number"] = negotiation_number
            df.drop(columns=['Market', 'Market Type', 'D/C'], inplace=True)
            df = df[["Data"] + ["Negotiation Number"] + [col for col in df.columns if col != "Data"]]
            df['Value Without Fee'] = df['Value Without Fee'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
            df['B/S'] = df['B/S'].replace({'C': 'B', 'V': 'S'})
            df['Ticker'] = df['Ticker'].str.extract(r'^(.{5}\d?)')

            # Compute sums for buys and sells
            buy_sum = df.loc[df['B/S'] == 'B', 'Value Without Fee'].sum()
            sell_sum = df.loc[df['B/S'] == 'S', 'Value Without Fee'].sum()
            base_total = buy_sum + sell_sum

            ## Calculate the proportional fee ("taxa")
            value_before_tax = abs(sell_sum - buy_sum)
            total_price_float = float(total_price.replace('.', '').replace(',', '.'))
            taxa = abs(abs(value_before_tax) - abs(total_price_float))

            # Apply fee proportionally to buys
            if buy_sum > 0:
                taxa_c = (df.loc[df['B/S'] == 'B', 'Value Without Fee'] / base_total) * taxa
                df.loc[df['B/S'] == 'B', 'Final Value'] = (df.loc[df['B/S'] == 'B', 'Value Without Fee'] + taxa_c).round(2)

             # Apply fee proportionally to sells
            if sell_sum > 0:
                taxa_v = (df.loc[df['B/S'] == 'S', 'Value Without Fee'] / base_total) * taxa
                df.loc[df['B/S'] == 'S', 'Final Value'] = (df.loc[df['B/S'] == 'S', 'Value Without Fee'] - taxa_v).round(2)
            return df
        
        except Exception as e:
            print(f"Could not extract data from file: {file}")
            print("Error:", e)
            traceback.print_exc() 
            return None

if __name__ == '__main__':
    GetNotesInfo()

