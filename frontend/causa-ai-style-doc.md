# 🎨 CLERK AI – Frontend Style Documentation

## 1. Color Palette
| Hex Code  | Usage |
|-----------|--------|
| `#130DDD` | Brand primary (logo, buttons, highlights) |
| `#111111` | Primary text, dark accents |
| `#FAFAFA` | Background (light sections) |
| `#FFFFFF` | Background (cards, panels, chat bubbles) |
| `#888888` | Secondary text, placeholders, icons |
| `#333333` | Body text, dividers |

---

## 2. Typography

- **Logo Font:**  
  - `Bodoni Moda SC` (Bold, All Caps)  
  - Usage: Header logo "CLERK"  

- **App Font (UI + body):**  
  - `Inter`  
  - Weight scale:  
    - Headings: `600–700`  
    - Body: `400–500`  
    - Captions: `400`  

- **Font Sizes (base: 16px):**  
  - H1: `32px` / `700`  
  - H2: `24px` / `600`  
  - Body: `16px` / `400–500`  
  - Small/Meta: `14px` / `400`  

---

## 3. Layout & Spacing

- **Grid:** 3-column layout  
  - Left sidebar → input + PDF upload  
  - Center → chat / welcome area  
  - Right sidebar → conversations / authentication  

- **Spacing scale (px):** `4, 8, 12, 16, 24, 32, 48`  
- **Max width:** `1440px`  
- **Dividers:** Thin, `#333333` @ 10–15% opacity  

---

## 4. Components

### 🔹 Header
- Background: `#FFFFFF`  
- Logo: `Bodoni Moda SC Bold`, `#130DDD`  
- Hamburger menu: `#111111`  

---

### 🔹 Left Sidebar
- **Case Input Box:**  
  - Background: `#F0EEFF` (tinted primary)  
  - Rounded corners: `8px`  
  - Font: Inter, `#111111`  

- **Upload Zone:**  
  - Background: `#FFFFFF`  
  - Border: `1px dashed #888888`  
  - Hover: `border-color: #130DDD`  

---

### 🔹 Main Chat Area
- **Welcome screen:**  
  - Title: Inter `24px / 600`  
  - Subtitle: Inter `16px / 400`, color `#333333`  

- **Message Bubbles:**  
  - User: `#FFFFFF` background, `#111111` text  
  - AI: `#F0EEFF` background, `#111111` text  
  - Rounded corners: `12px`  
  - Padding: `12–16px`  

- **Action Button (bottom):**  
  - Gradient: `linear-gradient(90deg, #130DDD, #8888FF)`  
  - Border radius: `12px`  
  - Text: Inter `16px / 500`, color `#FFFFFF`  

---

### 🔹 Right Sidebar
- **Authentication:**  
  - Background: `#FAFAFA` with diagonal stripe overlay (`#888888` @ 10–15%)  
  - Links:  
    - "Sign in" → Inter `16px`, `#111111`  
    - "Create account" → Inter `16px`, bold, `#130DDD` hover  

- **Conversations Panel (after login):**  
  - Header: Inter `16px / 600`  
  - Search field placeholder: `#888888`  
  - Conversation items: `#111111`, hover → `#FAFAFA`  
  - Close icons: `#888888`, hover → `#111111`  

---

## 5. States
- **Hover:**  
  - Buttons → darker gradient  
  - Links → underline  
- **Active:**  
  - Sidebar items → underline in `#130DDD`  
- **Disabled:**  
  - Opacity: `0.5`, cursor `not-allowed`  

---

## 6. React Implementation Notes
- **Component Structure:**
  - `Header`  
  - `SidebarLeft` (input, upload)  
  - `ChatWindow` (messages, input bar)  
  - `SidebarRight` (auth / conversations)  
  - `MessageBubble` (user vs AI)  
  - `UploadBox`  

- **Styling:**
  - Use Tailwind CSS with extended config:  
    ```js
    // tailwind.config.js
    module.exports = {
      theme: {
        extend: {
          colors: {
            brand: "#130DDD",
            dark: "#111111",
            light: "#FAFAFA",
            white: "#FFFFFF",
            gray: {
              DEFAULT: "#888888",
              dark: "#333333",
            },
          },
          fontFamily: {
            logo: ["'Bodoni Moda SC'", "serif"],
            sans: ["Inter", "sans-serif"],
          },
        },
      },
    }
    ```
  - Apply `font-logo` for header logo and `font-sans` for everything else.  
