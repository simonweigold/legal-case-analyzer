/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./src/index.html",
  ],
  theme: {
    extend: {
      colors: {
        // CAUSA AI Brand Colors
        brand: "#130DDD",
        dark: "#111111",
        light: "#FAFAFA",
        white: "#FFFFFF",
        gray: {
          DEFAULT: "#888888",
          dark: "#333333",
        },
        // Legacy shadcn/ui colors for components
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        chart: {
          "1": "hsl(var(--chart-1))",
          "2": "hsl(var(--chart-2))",
          "3": "hsl(var(--chart-3))",
          "4": "hsl(var(--chart-4))",
          "5": "hsl(var(--chart-5))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar))",
          foreground: "hsl(var(--sidebar-foreground))",
          primary: "hsl(var(--sidebar-primary))",
          "primary-foreground": "hsl(var(--sidebar-primary-foreground))",
          accent: "hsl(var(--sidebar-accent))",
          "accent-foreground": "hsl(var(--sidebar-accent-foreground))",
          border: "hsl(var(--sidebar-border))",
          ring: "hsl(var(--sidebar-ring))",
        },
      },
      fontFamily: {
        logo: ["'Bodoni Moda SC'", "serif"],
        sans: ["Inter", "sans-serif"],
        serif: ["var(--font-serif)"],
        mono: ["var(--font-mono)"],
      },
      fontSize: {
        'h1': ['32px', { lineHeight: '1.2', fontWeight: '700' }],
        'h2': ['24px', { lineHeight: '1.3', fontWeight: '600' }],
        'body': ['16px', { lineHeight: '1.5', fontWeight: '400' }],
        'small': ['14px', { lineHeight: '1.4', fontWeight: '400' }],
      },
      spacing: {
        '4px': '4px',
        '8px': '8px',
        '12px': '12px',
        '16px': '16px',
        '24px': '24px',
        '32px': '32px',
        '48px': '48px',
      },
      borderRadius: {
        'causa': '8px',
        'causa-lg': '12px',
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(90deg, #130DDD, #8888FF)',
      },
      maxWidth: {
        'app': '1440px',
      },
    },
  },
  plugins: [],
}
