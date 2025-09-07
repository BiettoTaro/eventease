"use client"

import Link from 'next/link'
import React from 'react'
import { usePathname } from 'next/navigation';

type NavbarItemProps = {
    title: string;
    address: string;

}

export default function NavbarItem({ title, address }: NavbarItemProps) {
    const pathname = usePathname();
    const isActive = pathname === address;
    return (
      <Link
        href={address}
        className={`dark:hover:text-orange-500 hover:text-gray-600 font-semibold transition-colors 
            ${isActive ? "underline underline-offset-8 decoration-4 decoration-orange-500 rounded-lg" : ""}`}
      >
        {title}
      </Link>
    );
  }