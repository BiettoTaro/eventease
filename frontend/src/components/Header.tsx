import React from 'react'
import HeaderItem from './HeaderItem'
import {AiFillHome} from 'react-icons/ai'
import { BsFillInfoCircleFill } from 'react-icons/bs'
import Link from 'next/link'

export default function Header() {
  return (
    <div className="flex justify-between items-center p-3 max-w-6xl mx-auto">
        <div className="flex gap-4">
            <HeaderItem title="Home" address="/" Icon={AiFillHome} />
            <HeaderItem title="About" address="/about" Icon={BsFillInfoCircleFill} />

        </div>
        <Link href="/">
            <span className="text-2xl font-bold bg-orange-500 py-1 px-2 rounded-lg">EventEase</span>
        </Link>
    </div>
  )
}
    