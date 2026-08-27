"use client"

import { AlertTriangle, AlertCircle, Info } from "lucide-react"

interface SeverityBannerProps {
  severity: string
  alerts: string[]
}

const severityConfig = {
  normal: {
    label: "Normal Conditions",
    color: "bg-green-100 border-green-500 text-green-900 dark:bg-green-900/30 dark:border-green-500 dark:text-green-100",
    icon: Info,
    show: false
  },
  warning: {
    label: "Weather Warning",
    color: "bg-yellow-100 border-yellow-500 text-yellow-900 dark:bg-yellow-900/30 dark:border-yellow-500 dark:text-yellow-100",
    icon: AlertTriangle,
    show: true
  },
  severe: {
    label: "Severe Weather Alert",
    color: "bg-orange-100 border-orange-500 text-orange-900 dark:bg-orange-900/30 dark:border-orange-500 dark:text-orange-100",
    icon: AlertTriangle,
    show: true
  },
  extreme: {
    label: "Extreme Weather Alert",
    color: "bg-red-100 border-red-500 text-red-900 dark:bg-red-900/30 dark:border-red-500 dark:text-red-100",
    icon: AlertCircle,
    show: true
  }
}

export default function SeverityBanner({ severity, alerts }: SeverityBannerProps) {
  const config = severityConfig[severity as keyof typeof severityConfig] || severityConfig.normal

  if (!config.show || alerts.length === 0) {
    return null
  }

  const Icon = config.icon

  return (
    <div className={`border-l-4 p-4 rounded-r-xl ${config.color} animate-pulse-subtle`}>
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-semibold">{config.label}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-white/50 dark:bg-white/10">
              {alerts.length} alert{alerts.length > 1 ? 's' : ''}
            </span>
          </div>
          <ul className="space-y-1">
            {alerts.map((alert, index) => (
              <li key={index} className="text-sm flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" />
                {alert}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}