"use client"

import { useTheme } from "next-themes";
import { useState, useEffect } from "react";

export default function DarkModeToggle() {
    const { theme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    // Avoid hydration mismatch
    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return null;
    }

    return (
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="px-3 py-2 rounded-md border bg-gray-200 dark:bg-gray-700 dark:text-white transition-colors"
        >
          {theme === "dark" ? "🌙 Dark" : "☀️ Light"}
        </button>
      );
}
