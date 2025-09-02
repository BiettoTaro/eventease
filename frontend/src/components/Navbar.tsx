import React from 'react'
import NavbarItem from './NavbarItem'

export default function Navbar() {
  return (
    <div className='flex gap-6 p-4 max-w-6xl mx-auto dark:bg-gray-600 bg-orange-500 lg:text-lg justify-center'>
        <NavbarItem title="News" address="/news"/>
        <NavbarItem title="Events" address="/events"/>
    </div>
  )
}
