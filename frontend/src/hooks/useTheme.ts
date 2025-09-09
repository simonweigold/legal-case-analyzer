// hooks/useTheme.ts
import { useState, useEffect } from 'react';
import { createTheme, useMediaQuery } from '@mui/material';

export function useTheme() {
  const prefersDark = useMediaQuery('(prefers-color-scheme: dark)');
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    return saved ? JSON.parse(saved) : prefersDark;
  });

  useEffect(() => {
    localStorage.setItem("darkMode", JSON.stringify(darkMode));
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [darkMode]);

  const theme = createTheme({
    palette: {
      mode: darkMode ? "dark" : "light",
      primary: { 
        main: "#1976d2"
      },
      secondary: {
        main: "#dc004e"
      },
      background: { 
        default: darkMode ? "#121212" : "#fafafa",
        paper: darkMode ? "#1e1e1e" : "#ffffff"
      },
    },
    shape: { borderRadius: 8 },
    components: {
      MuiPaper: {
        styleOverrides: { 
          root: { 
            borderRadius: 8,
            border: `1px solid ${darkMode ? '#333' : '#e0e0e0'}`
          } 
        },
      },
      MuiButton: {
        defaultProps: { variant: "contained" },
      },
    },
  });

  // Set CSS variables for theme
  useEffect(() => {
    document.documentElement.style.setProperty(
      "--background-color",
      theme.palette.background.default
    );
    document.documentElement.style.setProperty(
      "--text-color",
      theme.palette.text.primary
    );
  }, [theme]);

  const toggleDarkMode = () => setDarkMode((prev: boolean) => !prev);

  return {
    theme,
    darkMode,
    toggleDarkMode
  };
}
