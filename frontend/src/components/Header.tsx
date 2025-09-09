"use client"

import React from 'react'
import HeaderItem from './HeaderItem'
import {AiFillHome} from 'react-icons/ai'
import { BsFillInfoCircleFill } from 'react-icons/bs'
import { FiLogOut } from 'react-icons/fi'
import Link from 'next/link'
import DarkModeToggle from './DarkModeToggle'
import { logout } from '../lib/api'
import { useRouter } from 'next/navigation'

export default function Header() {
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <div className="flex justify-between items-center p-3 max-w-6xl mx-auto">
        <div className="flex gap-4">
            <HeaderItem title="Home" address="/" Icon={AiFillHome} />
            <HeaderItem title="About" address="/about" Icon={BsFillInfoCircleFill} />
            <HeaderItem title="Logout" Icon={FiLogOut} onClick={handleLogout} /> 
        </div>
        <div className="flex gap-4 items-center">
          <DarkModeToggle />
          <Link href="/">
              <span className="text-2xl font-bold bg-orange-500 py-1 px-2 rounded-lg">EventEase</span>
          </Link>
        </div>
    </div>
  )
}
    