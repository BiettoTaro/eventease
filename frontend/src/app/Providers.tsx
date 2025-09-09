"use client"

import { ThemeProvider } from "next-themes"
import { AuthProvider } from "../context/AuthContext"
import React from 'react'

type Props = {
    children: React.ReactNode
}

export default function Providers({ children }: Props) {
  return (
    <ThemeProvider defaultTheme="system" enableSystem attribute="class">
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  )
}
