import os
from mlx_lm import load, generate
from datetime import datetime
from pyfastic.config import settings

class MarkdownTranslator:
    def __init__(self, model_path=settings.TRANSLATION_MODEL):
        print(f"Laden van model: {model_path}...")
        self.model, self.tokenizer = load(model_path)
        self.max_tokens = 2048

    def chunk_text(self, text, max_chars=3000):
        """
        Splitst tekst op basis van regeleinden om te voorkomen dat zinnen 
        of paragrafen middenin worden afgebroken.
        """
        if len(text) <= max_chars:
            return [text]

        chunks = []
        while text:
            # Als de resterende tekst kleiner is dan de limiet, zijn we klaar
            if len(text) <= max_chars:
                chunks.append(text.strip())
                break
            
            # Zoek het laatste regeleinde binnen het limiet van max_chars
            # We zoeken naar \n zodat we paragrafen of zinnen respecteren
            split_index = text.rfind('\n', 0, max_chars)
            
            # Als er geen regeleinde gevonden is (bijv. één hele lange zin), 
            # zoek dan naar een spatie om tenminste woorden heel te houden
            if split_index == -1:
                split_index = text.rfind(' ', 0, max_chars)
                
            # Als er echt niets te vinden is, knip dan hard op max_chars
            if split_index == -1:
                split_index = max_chars

            # Voeg de chunk toe en kort de brontekst in voor de volgende ronde
            chunks.append(text[:split_index].strip())
            text = text[split_index:].lstrip()


        return chunks

    def translate_chunk(self, text):
        """Vertaalt een specifiek tekstblok."""
        prompt = (
            "Translate the following Dutch text to English. "
            "Only output the translated text:\n\n"
            f"{text}"
        )
        
        if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template is not None:
            messages = [{"role": "user", "content": prompt}]
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

        # We zetten verbose=False om de console schoon te houden tijdens het proces
        return generate(
            self.model, 
            self.tokenizer, 
            prompt=prompt, 
            verbose=False, 
            max_tokens=self.max_tokens
        )

    def translate_file(self, input_path, output_path, max_chunk_size=3000):
        if not os.path.exists(input_path):
            print(f"Fout: {input_path} niet gevonden.")
            return

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Stap 1: Splits de tekst in behapbare stukken
        chunks = self.chunk_text(content, max_chars=max_chunk_size)
        print(f"Bestand gesplitst in {len(chunks)} stukken. Start vertaling...")

        translated_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"Bezig met stuk {i+1}/{len(chunks)}...")
            translated_text = self.translate_chunk(chunk)
            translated_chunks.append(translated_text)

        # Stap 2: Voeg alles weer samen en sla op
        final_output = "\n\n".join(translated_chunks)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_output)
        
        print(f"Klaar! Vertaling opgeslagen in: {output_path}")

# --- Voorbeeldgebruik ---
if __name__ == "__main__":
    start = datetime.now()
    print(f"Start vertaling van Markdown bestand...{start.strftime('%Y-%m-%d %H:%M:%S')}")
    translator = MarkdownTranslator()
    # Je kunt de max_chunk_size aanpassen op basis van je VRAM
    translator.translate_file("small_book.md", "final_vertaling.md", max_chunk_size=1000)

    
    # with open("book.md", 'r', encoding='utf-8') as r:
    #     content=r.read()
    # final_output = translator.chunk_text(content, max_chars=1000)

    # with open("out1.md", 'w', encoding='utf-8') as f:
    #     for i, fo in enumerate(final_output):
    #         f.write(f"=========================== Chunk {i+1}:\n{str(fo)}\n\n")
    end = datetime.now()
    print(f"Einde vertaling...{end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tijd genomen: {end - start}")