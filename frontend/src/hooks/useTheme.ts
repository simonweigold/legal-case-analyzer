// hooks/useTheme.ts
import { useState, useEffect, useMemo } from 'react';
import { createTheme, useMediaQuery } from '@mui/material';

// Helper function to get CSS variable value
const getCSSVariable = (variable: string): string => {
  if (typeof window !== 'undefined') {
    return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
  }
  return '';
};

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

  // Create theme with CSS variables designed for Material-UI compatibility
  const theme = useMemo(() => {
    // Get Material-UI compatible CSS variable values
    const background = getCSSVariable('--mui-background') || (darkMode ? '#252525' : '#bbbbbb');
    const foreground = getCSSVariable('--mui-foreground') || (darkMode ? '#fcfcfc' : '#404040');
    const card = getCSSVariable('--mui-card') || (darkMode ? '#353535' : '#bbbbbb');
    const primary = getCSSVariable('--mui-primary') || (darkMode ? '#ebebeb' : '#404040');
    const secondary = getCSSVariable('--mui-secondary') || (darkMode ? '#454545' : '#f7f7f7');
    const border = getCSSVariable('--mui-border') || (darkMode ? '#474747' : '#f7f7f7');
    const mutedForeground = getCSSVariable('--mui-muted-foreground') || (darkMode ? '#b5b5b5' : '#8e8e8e');

    return createTheme({
    palette: {
      mode: darkMode ? "dark" : "light",
      primary: { 
        main: primary
      },
      secondary: {
        main: secondary
      },
      background: { 
        default: background,
        paper: card
      },
      text: {
        primary: foreground,
        secondary: mutedForeground
      },
      divider: border,
    },
    shape: { borderRadius: 10 }, // Using number for MUI, CSS var applied in component overrides
    components: {
      MuiPaper: {
        styleOverrides: { 
          root: { 
            borderRadius: "var(--radius)",
            border: "1px solid var(--border)",
            backgroundColor: "var(--card)",
            color: "var(--card-foreground)"
          } 
        },
      },
      MuiButton: {
        defaultProps: { variant: "contained" },
        styleOverrides: {
          root: {
            borderRadius: "var(--radius)",
          }
        }
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              backgroundColor: "var(--input)",
              borderRadius: "var(--radius)",
              '& fieldset': {
                borderColor: "var(--border)",
              },
              '&:hover fieldset': {
                borderColor: "var(--ring)",
              },
              '&.Mui-focused fieldset': {
                borderColor: "var(--ring)",
              },
            },
          },
        },
      },
    },
  });
  }, [darkMode]); // Recreate theme when darkMode changes

  const toggleDarkMode = () => setDarkMode((prev: boolean) => !prev);

  return {
    theme,
    darkMode,
    toggleDarkMode
  };
}
