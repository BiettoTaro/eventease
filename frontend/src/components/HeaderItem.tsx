import React from "react";
import Link from "next/link";
import { IconType } from "react-icons";

type HeaderItemProps = {
  title: string;
  address?: string;   // optional for actions like logout
  Icon: IconType;
  onClick?: () => void; // optional action
};

export default function HeaderItem({ title, address, Icon, onClick }: HeaderItemProps) {
  const classes = "hover:text-orange-500 flex items-center space-x-2";

  if (onClick) {
    return (
      <button onClick={onClick} className={classes}>
        <Icon className="text-2xl sm:hidden" />
        <p className="uppercase hidden sm:inline text-sm">{title}</p>
      </button>
    );
  }

  return (
    <Link href={address || "#"} className={classes}>
      <Icon className="text-2xl sm:hidden" />
      <p className="uppercase hidden sm:inline text-sm">{title}</p>
    </Link>
  );
}
