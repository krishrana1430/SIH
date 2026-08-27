"use client"

import { useState } from "react"
import { MapPin, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

interface Location {
  name: string
  state: string
  lat: number
  lng: number
}

interface LocationSelectorProps {
  locations: Location[]
  selectedLocation: string
  onSelect: (location: string) => void
}

export default function LocationSelector({
  locations,
  selectedLocation,
  onSelect,
}: LocationSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className="w-full justify-between"
        >
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-gray-500" />
            <span className="text-sm">
              {selectedLocation || "Select Location"}
            </span>
          </div>
          <ChevronDown className="w-4 h-4 text-gray-500" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[300px] p-0" align="start">
        <div className="max-h-[300px] overflow-y-auto">
          {locations.map((location) => (
            <button
              key={location.name}
              onClick={() => {
                onSelect(location.name)
                setIsOpen(false)
              }}
              className={`w-full px-4 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${
                selectedLocation === location.name
                  ? 'bg-blue-50 dark:bg-blue-900/20'
                  : ''
              }`}
            >
              <div className="font-medium text-gray-900 dark:text-white">
                {location.name}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-200">
                {location.state}
              </div>
            </button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  )
}
