"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export default function PageContainer({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [displayed, setDisplayed] = useState(children);
  const previousPath = useRef(pathname);

  useEffect(() => {
    if (pathname !== previousPath.current) {
      // Route changed → keep old children until new ones render
      previousPath.current = pathname;
      setDisplayed(children);
    } else {
      // Same route → update normally
      setDisplayed(children);
    }
  }, [pathname, children]);

  return <div className="min-h-screen">{displayed}</div>;
}
