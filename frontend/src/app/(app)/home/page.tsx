"use client";

import React from 'react'
import {useEffect} from 'react'

export default function Home() {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return; //  don’t ask location if not logged in

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          console.log("User location: ", lat, lng);

          fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/users/me/location`, {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ latitude: lat, longitude: lng }),
          });
        },
        (error) => {
          console.error("Error getting location:", error);
        }
      );
    }
  }, []);


  return  (
    <div className="p-10 text-center">
    <h1 className="text-3xl font-bold mb-4 text-orange-500">Welcome to EventEase</h1>
    <p className="text-lg text-gray-700 dark:text-gray-300">
      Browse the latest <span className="font-semibold">News</span> or upcoming{" "}
      <span className="font-semibold">Events</span> using the navigation above.
    </p>
  </div>
  )
}
          