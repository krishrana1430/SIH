"use client"

import { useState, useCallback } from "react"
import { Send, Mic, Sparkles, Bot, User, Shield } from "lucide-react"
import { Button } from "@/components/ui/button"
import { askWeatherQuestion, AskResponse } from "@/lib/api"

interface Message {
  role: 'user' | 'assistant'
  content: string
  metadata?: {
    severity?: string
    llm_tier?: string | null
    intent?: string
    role?: string
  }
}

interface ChatInterfaceProps {
  location: string
  role: string
  language: string
}

export default function ChatInterface({ location, role, language }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Hello! I'm WeatherGPT, your AI weather assistant. Ask me about the weather in ${location} or any other weather-related questions!`
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  const handleSend = useCallback(async () => {
    if (!input.trim()) return

    const userMsg = input
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setInput('')
    setIsTyping(true)

    try {
      const result: AskResponse = await askWeatherQuestion(userMsg, language, role)

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: result.response,
        metadata: {
          severity: result.severity.severity,
          llm_tier: result.llm_tier_used,
          intent: result.intent.intent,
          role: result.role
        }
      }])
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred'
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Sorry, I couldn't process your request: ${errorMessage}. Please try again.`,
        metadata: {
          severity: 'normal',
          llm_tier: null
        }
      }])
    } finally {
      setIsTyping(false)
    }
  }, [input, language, role])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="space-y-3">
      <div className="space-y-2 max-h-[300px] overflow-y-auto">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-xl px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              {msg.role === 'assistant' && msg.metadata && (
                <div className="flex items-center gap-2 mt-2 text-xs opacity-70">
                  {msg.metadata.severity && msg.metadata.severity !== 'normal' && (
                    <Shield className="w-3 h-3" />
                  )}
                  {msg.metadata.llm_tier && (
                    <span className="px-1.5 py-0.5 rounded bg-white/20 dark:bg-white/10 text-[10px]">
                      {msg.metadata.llm_tier}
                    </span>
                  )}
                  {msg.metadata.intent && (
                    <span className="px-1.5 py-0.5 rounded bg-white/20 dark:bg-white/10 text-[10px]">
                      {msg.metadata.intent}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-xl px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <div className="flex-1 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask about weather in ${location}...`}
            className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-800 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
            disabled={isTyping}
          />
          <button className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50" disabled={isTyping}>
            <Mic className="w-4 h-4" />
          </button>
        </div>
        <Button onClick={handleSend} className="rounded-full" disabled={isTyping || !input.trim()}>
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}