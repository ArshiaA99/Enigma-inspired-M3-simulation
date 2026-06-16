from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="Enigma Cipher Engine")

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
ROTORS = {
    "I":   "ekmflgdqvzntowyhxuspaibrcj",
    "II":  "ajdksiruxblhwtmcqgznpyfvoe",
    "III": "bdfhjlcprtxvznyeiwgakmusqo",
    "IV":  "esovpzjayquirhxlnftgkdcmwb",
    "V":   "vzbrgityupsdnhlxawmjqofeck"
}
REFLECTOR_B = "yruhqsldpxngokmiebfzcwvjat"

def build_plugboard(text: str) -> dict:
    plugboard = {}
    pairs = text.upper().split()
    for pair in pairs:
        if len(pair) != 2:
            raise ValueError(f"Invalid pair length: {pair}")
        a, b = pair.lower()
        if a == b:
            raise ValueError(f"Self-connecting pair invalid: {pair}")
        if a in plugboard or b in plugboard:
            raise ValueError(f"Duplicate connection for letter in pair: {pair}")
        plugboard[a] = b
        plugboard[b] = a
    return plugboard

def plug_swap(c: str, plugboard: dict) -> str:
    return plugboard.get(c, c)

def reflector(c: str) -> str:
    return REFLECTOR_B[ALPHABET.find(c)]

def encrypt_message(text: str, rotor_names: list, plugboard: dict) -> str:
    r1 = ROTORS[rotor_names[0]]
    r2 = ROTORS[rotor_names[1]]
    r3 = ROTORS[rotor_names[2]]

    state = 0
    cipher = ""

    def rotate_rotors():
        nonlocal r1, r2, r3, state
        r1 = r1[1:] + r1[0]
        if state % 26 == 0:
            r2 = r2[1:] + r2[0]
        if state % (26 * 26) == 0:
            r3 = r3[1:] + r3[0]

    def enigma_one_char(c: str) -> str:
        if c not in ALPHABET:
            return c

        c = plug_swap(c, plugboard)
        c1 = r1[ALPHABET.find(c)]
        c2 = r2[ALPHABET.find(c1)]
        c3 = r3[ALPHABET.find(c2)]

        reflected = reflector(c3)

        c3 = ALPHABET[r3.find(reflected)]
        c2 = ALPHABET[r2.find(c3)]
        c1 = ALPHABET[r1.find(c2)]
        c1 = plug_swap(c1, plugboard)
        return c1

    for ch in text.lower():
        if ch in ALPHABET:
            state += 1
            cipher += enigma_one_char(ch)
            rotate_rotors()
        else:
            cipher += ch

    return cipher.upper()


class CipherRequest(BaseModel):
    text: str = Field(..., example="The enigma engine is operational.")
    rotors: list[str] = Field(..., max_items=3, min_items=3, example=["I", "II", "III"])
    plugboard: str = Field(default="", example="AM FT PX")

@app.post("/api/cipher")
def process_cipher(payload: CipherRequest):
    # Validate unique rotors selection
    if len(set(payload.rotors)) != 3:
        raise HTTPException(status_code=400, detail="Please select three distinct rotors.")
    
    try:
        plugboard_matrix = build_plugboard(payload.plugboard)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be blank.")

    result = encrypt_message(payload.text, payload.rotors, plugboard_matrix)
    return {"success": True, "result": result}


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enigma Machine Web UI</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; }
            .mono { font-family: 'JetBrains Mono', monospace; }
        </style>
    </head>
    <body class="bg-[#0B0F19] text-slate-100 min-h-screen flex flex-col justify-between">

        <header class="border-b border-slate-800/60 bg-[#0F172A]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
            <div class="max-w-6xl mx-auto flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="h-3 w-3 rounded-full bg-cyan-400 animate-pulse"></div>
                    <span class="text-lg font-extrabold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mono">
                        ENIGMA M3 // WEB_ENGINE
                    </span>
                </div>
                <span class="text-xs text-slate-500 bg-slate-900 px-3 py-1.5 rounded-md border border-slate-800 mono">STATUS: ACTIVE</span>
            </div>
        </header>

        <main class="max-w-6xl w-full mx-auto p-4 md:p-8 grid grid-cols-1 lg:grid-cols-12 gap-8 flex-grow items-start">
            
            <div class="lg:col-span-5 space-y-6">
                
                <div class="bg-[#111827] border border-slate-800/80 rounded-2xl p-6 shadow-xl">
                    <h2 class="text-xs font-bold tracking-widest text-cyan-400 uppercase mb-4 flex items-center">
                        <span class="mr-2">//</span> Rotor Configuration
                    </h2>
                    <div class="grid grid-cols-3 gap-3">
                        <div>
                            <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1.5 text-center">Left</label>
                            <select id="rotor1" class="w-full bg-[#1F2937] border border-slate-700/80 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500 cursor-pointer text-center">
                                <option value="I" selected>I</option>
                                <option value="II">II</option>
                                <option value="III">III</option>
                                <option value="IV">IV</option>
                                <option value="V">V</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1.5 text-center">Middle</label>
                            <select id="rotor2" class="w-full bg-[#1F2937] border border-slate-700/80 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500 cursor-pointer text-center">
                                <option value="I">I</option>
                                <option value="II" selected>II</option>
                                <option value="III">III</option>
                                <option value="IV">IV</option>
                                <option value="V">V</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1.5 text-center">Right</label>
                            <select id="rotor3" class="w-full bg-[#1F2937] border border-slate-700/80 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500 cursor-pointer text-center">
                                <option value="I">I</option>
                                <option value="II">II</option>
                                <option value="III" selected>III</option>
                                <option value="IV">IV</option>
                                <option value="V">V</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="bg-[#111827] border border-slate-800/80 rounded-2xl p-6 shadow-xl">
                    <div class="flex justify-between items-center mb-2">
                        <h2 class="text-xs font-bold tracking-widest text-cyan-400 uppercase flex items-center">
                            <span class="mr-2">//</span> Plugboard Matrix
                        </h2>
                        <span class="text-[10px] text-slate-500 italic">Space separated</span>
                    </div>
                    <input type="text" id="plugboard" value="AM FT PX" placeholder="e.g. AB CD EF" 
                        class="w-full bg-[#1F2937] border border-slate-700/80 rounded-xl px-4 py-3 text-sm tracking-widest font-bold text-emerald-400 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500 uppercase mono">
                </div>

                <div class="bg-[#111827]/60 border border-slate-800/40 rounded-2xl p-4 shadow-xl hidden md:block">
                    <div class="flex items-center justify-between text-[11px] text-slate-500 mono">
                        <span>IN ──► PLUG ──► R1 ──► R2 ──► R3</span>
                        <span class="text-pink-500">▼</span>
                    </div>
                    <div class="flex items-center justify-between text-[11px] text-slate-500 mt-1 mono">
                        <span>OUT ◄── PLUG ◄── R1 ◄── R2 ◄── R3 ◄── REFL</span>
                    </div>
                </div>
            </div>

            <div class="lg:col-span-7 flex flex-col space-y-6 h-full">
                
                <div class="bg-[#111827] border border-slate-800/80 rounded-2xl p-6 shadow-xl flex flex-col flex-grow">
                    <label class="block text-xs font-bold tracking-widest text-slate-400 uppercase mb-3">// INPUT PLAINTEXT</label>
                    <textarea id="plaintext" rows="4" placeholder="Type your secret transmission here..." 
                        class="w-full bg-[#0B0F19] border border-slate-800 rounded-xl p-4 text-base text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500 resize-none flex-grow min-h-[120px]"></textarea>
                </div>

                <button onclick="processCipher()" 
                    class="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 active:scale-[0.99] text-slate-950 text-sm font-extrabold tracking-widest uppercase py-4 px-6 rounded-xl transition-all duration-150 shadow-lg shadow-cyan-500/10 hover:shadow-cyan-400/20 flex items-center justify-center space-x-2">
                    <span>EXECUTE CIPHER RE-ROUTING</span>
                </button>

                <div class="bg-[#111827] border border-slate-800/80 rounded-2xl p-6 shadow-xl flex flex-col flex-grow">
                    <div class="flex justify-between items-center mb-3">
                        <label class="block text-xs font-bold tracking-widest text-amber-400 uppercase">// OUTPUT CIPHERTEXT</label>
                        <button onclick="copyOutput()" class="text-[10px] text-slate-400 hover:text-cyan-400 underline cursor-pointer transition-colors">Copy</button>
                    </div>
                    <textarea id="ciphertext" rows="4" readonly placeholder="Output processing matrix..." 
                        class="w-full bg-[#0B0F19] border border-slate-800 rounded-xl p-4 text-base font-bold text-amber-400 placeholder-slate-700/60 focus:outline-none resize-none flex-grow min-h-[120px] tracking-wider mono"></textarea>
                </div>
            </div>
        </main>

        <footer class="text-center py-4 border-t border-slate-900 text-[11px] text-slate-600 font-medium tracking-wide mono">
            ENIGMA M3 CIPHER SIMULATOR // 2026
        </footer>

        <script>
            async function processCipher() {
                const text = document.getElementById('plaintext').value;
                const rotors = [
                    document.getElementById('rotor1').value,
                    document.getElementById('rotor2').value,
                    document.getElementById('rotor3').value
                ];
                const plugboard = document.getElementById('plugboard').value;
                const outputField = document.getElementById('ciphertext');

                try {
                    const response = await fetch('/api/cipher', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text, rotors, plugboard })
                    });

                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || "An unexpected system anomaly occurred.");
                    }

                    outputField.value = data.result;
                } catch (error) {
                    alert("Execution Refused:\\n" + error.message);
                }
            }

            function copyOutput() {
                const copyText = document.getElementById("ciphertext");
                if(!copyText.value) return;
                copyText.select();
                copyText.setSelectionRange(0, 99999);
                navigator.clipboard.writeText(copyText.value);
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
