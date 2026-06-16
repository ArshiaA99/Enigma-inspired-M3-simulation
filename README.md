# 🔐 Enigma M3 Cipher Engine

A modern web-based simulation of the famous **Enigma M3 Machine**, implemented with **Python**, **FastAPI**, and a responsive browser interface.

This project recreates the core concepts of the historical German Enigma cipher system, including multiple rotors, a reflector, rotor stepping, and a configurable plugboard. Users can encrypt and decrypt messages directly through a web interface or via a REST API.

---

## 🧠 What Was the Enigma Machine?

The **Enigma Machine** was an electromechanical encryption device used extensively by German military forces during World War II.

When an operator pressed a key:

1. The signal first passed through a **plugboard**, swapping selected letter pairs.
2. It then traveled through multiple **rotors**, each performing a substitution.
3. The signal reached a **reflector**, which redirected it back through the rotors.
4. The output letter illuminated on the lampboard.
5. The rotors rotated after each keypress, continuously changing the encryption pattern.

Because of the reflector design, the same machine configuration could both encrypt and decrypt messages.

---

## ⚙️ Features

### Historical Rotor Set

Includes the authentic Wehrmacht rotor wirings:

* Rotor I
* Rotor II
* Rotor III
* Rotor IV
* Rotor V

Users may select any three distinct rotors for encryption.

---

### Reflector B

Implements the historical **Reflector B** wiring used in many Enigma configurations.

---

### Plugboard Support

Configure custom plugboard connections such as:

AB CD EF

The plugboard performs substitutions both before entering and after exiting the rotor system, significantly increasing cipher complexity.

---

### Rotor Stepping Mechanism

After each encrypted character:

* Rotor I rotates every keypress.
* Rotor II rotates after a full revolution of Rotor I.
* Rotor III rotates after a full revolution of Rotor II.

This creates a continuously changing encryption state.

---

### FastAPI REST API

Encrypt messages programmatically through a simple JSON API.

#### Endpoint

POST `/api/cipher`

#### Example Request

```json
{
    "text": "HELLO WORLD",
    "rotors": ["I", "II", "III"],
    "plugboard": "AM FT PX"
}
```

#### Example Response

```json
{
    "success": true,
    "result": "..."
}
```

---

### Modern Web Interface

The project includes a responsive browser-based UI featuring:

* Rotor selection controls
* Plugboard configuration
* Plaintext input
* Ciphertext output
* One-click copy functionality
* Real-time API integration

---

## 🔄 Encryption and Decryption

Like the original Enigma machine, encryption is symmetric.

Using:

* The same rotor order
* The same plugboard configuration
* The same starting rotor positions

Running ciphertext through the machine again will reproduce the original plaintext.

---

## 🚀 Running the Project

### Install Dependencies

```bash
pip install fastapi uvicorn pydantic
```

### Start the Server

```bash
python main.py
```

The application will be available at:

```text
http://127.0.0.1:8000
```

Open the URL in your browser to access the Enigma web interface.

---

## 🏗 Project Architecture

```text
Client Browser
      │
      ▼
 FastAPI Web Server
      │
      ▼
 Enigma Cipher Engine
      │
 ├── Plugboard
 ├── Rotor I–V
 ├── Reflector B
 └── Rotor Stepping Logic
```

---

## 📚 Educational Purpose

This project is designed for educational and demonstration purposes.

While inspired by the historical Enigma machine, it is a simplified software implementation intended to help students understand:

* Classical cryptography
* Substitution ciphers
* Rotor-based encryption systems
* Symmetric encryption concepts
* API development with FastAPI

---

## 👨‍💻 Author

**Arshia Karkhanehie**

GitHub: https://github.com/ArshiaA99
