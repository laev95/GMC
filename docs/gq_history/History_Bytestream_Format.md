# GMC History Bytestream Format

This document describes the structure and rules of a complete GMC history
bytestream: what patterns can appear, in what order, and how the stream is
logically divided.

---

## 1. Stream Structure

- The bytestream consists of **0..N records** concatenated back-to-back.
- A **record boundary** is defined by a *valid header*.
- The byte sequence `55 aa 00` may appear inside data; **it only starts a new
  record when it forms a valid header**.

---

## 2. Record Header Format (Mandatory)

Every record starts with exactly:

- **Header prefix:** `55 aa 00` (three bytes)
- **Timestamp:** (six bytes)
- **Save-type token:** `55 aa xx` (three bytes)

### Header layout

```
55 aa 00 + <6 bytes date> + <3 bytes save_type_token>
```

### Save-type token values

The save-type token defines how many tubes or channels were active when the
record was saved.

| Token      | Meaning                           |
|------------|-----------------------------------|
| `55 aa 00` | off                               |
| `55 aa 01` | save every second                 |
| `55 aa 02` | save every minute                 |
| `55 aa 03` | save every hour (average)         |
| `55 aa 04` | save every second after threshold |
| `55 aa 05` | save every minute after threshold |

---

## 3. Record Body Structure

After the header, the record body is a **token/value stream**, not a single
continuous blob.

The body continues until:
- the next valid record header, or
- end-of-stream.

The body may contain a mixture of:

- **Special tokens** (`55 aa 01` .. `55 aa 05`) that change interpretation
  rules or metadata.
- **Measurement bytes**, whose width depends on the current reading mode.
- **ASCII payload bytes**, but only while in ASCII mode.

---

## 4. Special Tokens (Body Interpretation)

Inside a record body, the following 3-byte special tokens may appear at any time:

| Token      | Meaning        |
|------------|----------------|
| `55 aa 01` | double         |
| `55 aa 02` | ascii          |
| `55 aa 03` | triple         |
| `55 aa 04` | quadruple      |
| `55 aa 05` | tube selection |

Special tokens may occur:
- immediately after the header
- between measurements
- multiple times within a single record

---

## 5. Tube Selection (Special Case)

- When the token `55 aa 05` appears, it is **always followed by one extra byte**.
- This byte selects which tube(s) later data belongs to.

### Tube ID values

| Byte | Meaning |
|------|---------|
| `00` | both    |
| `01` | tube 1  |
| `02` | tube 2  |

### Pattern

```
55 aa 05 + <1 byte tube_id>
```

### Persistence

- Tube selection **persists across records**.
- If a record does not contain a tube token, it **inherits the last selected
  tube** from earlier in the stream.

---

## 6. Default Mode at Record Start

- When a new header is read, the measurement mode resets to **SINGLE**
  (1-byte values).
- Measurement width changes are driven solely by special tokens in the body.

---

## 7. Measurement Encoding (Numeric Mode)

While in numeric mode, the body contains a run of **unsigned integers**
encoded as raw bytes:

| Mode        | Bytes per value |
|-------------|-----------------|
| SINGLE      | 1 byte          |
| DOUBLE      | 2 bytes         |
| TRIPLE      | 3 bytes         |
| QUADRUPLE   | 4 bytes         |

Measurement runs may be interrupted at any time by:
- a special token (`55 aa 01` .. `55 aa 05`)
- the next valid record header

---

## 8. ASCII Mode Encoding

- ASCII mode begins after the token `55 aa 02`.
- In ASCII mode, the payload consists of raw bytes expected to be ASCII text.
- ASCII mode ends when the next recognizable control sequence begins:
  - a special token (`55 aa 01` .. `55 aa 05`), or
  - the next record header (`55 aa 00 + date6 + save_type_token`)

---

## 9. Record and Stream Termination

- A record ends when the next valid header begins.
- The device does **not** emit an explicit end-of-recording marker.
- When the internal history buffer is not fully used, the device fills the
  remaining bytes with the value `0xFF` (`255`).

