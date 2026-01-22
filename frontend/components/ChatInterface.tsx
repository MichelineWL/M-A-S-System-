"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  User,
  Bot,
  Loader2,
  BarChart2,
  Sparkles,
  CheckCircle2,
  Brain,
  Zap,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { api, ExecutionResult, Visualization, ExecutionPlan } from "@/lib/api";
import ChartRenderer from "@/components/ChartRenderer";
import { cn } from "@/lib/utils";

// Available Gemini models (Jan 2026 - Verified from Google AI Studio)
const GEMINI_MODELS = [
  {
    value: "gemini-2.0-flash",
    label: "⚡ Gemini 2.0 Flash",
    description: "2K RPM, Unlimited RPD (Recommended)",
  },
  {
    value: "gemini-2.5-flash-lite",
    label: "🚀 Gemini 2.5 Flash Lite",
    description: "4K RPM, Unlimited RPD (Fastest)",
  },
  {
    value: "gemini-2.5-flash",
    label: "✨ Gemini 2.5 Flash",
    description: "1K RPM, High performance",
  },
  {
    value: "gemini-3-flash",
    label: "🔥 Gemini 3 Flash",
    description: "1K RPM, Latest generation",
  },
  {
    value: "gemini-2.5-pro",
    label: "💎 Gemini 2.5 Pro",
    description: "150 RPM, Most powerful",
  },
];

interface Message {
  role: "user" | "assistant";
  content: string;
  plan?: ExecutionPlan;
  visualization?: Visualization;
  timestamp: Date;
}

interface ChatInterfaceProps {
  sessionId: string;
}

export default function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I've analyzed your data. Ask me anything about it, or tell me to create a chart! 📊",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState("gemini-2.0-flash");
  const [showMode, setShowMode] = useState<"both" | "thinking" | "doing">(
    "both",
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput("");

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessage,
        timestamp: new Date(),
      },
    ]);

    setIsLoading(true);

    try {
      const response = await api.query(sessionId, userMessage, selectedModel);

      // Add AI response with plan
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.result.answer,
          plan: response.plan,
          visualization: response.result.visualization,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error("Query error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error processing your request.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] w-full max-w-4xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={cn(
              "flex w-full",
              msg.role === "user" ? "justify-end" : "justify-start",
            )}
          >
            <div
              className={cn(
                "flex max-w-[80%] md:max-w-[70%] rounded-lg px-4 py-3 shadow-sm",
                msg.role === "user"
                  ? "bg-primary text-primary-foreground ml-12"
                  : "bg-muted text-foreground mr-12",
              )}
            >
              <div className="flex flex-col w-full gap-2">
                <div className="flex items-center gap-2 mb-1 opacity-70 text-xs uppercase tracking-wider font-semibold">
                  {msg.role === "user" ? <User size={12} /> : <Bot size={12} />}
                  <span>{msg.role === "assistant" ? "AI Analyst" : "You"}</span>
                </div>

                {/* Multi-Agent Workflow */}
                {msg.plan && (
                  <div className="mb-4 space-y-3">
                    {/* Multi-Agent Header */}
                    <div className="flex items-center gap-2 text-xs font-semibold text-primary">
                      <Users size={14} />
                      <span>MULTI-AGENT WORKFLOW</span>
                    </div>

                    {/* Understanding */}
                    <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-md">
                      <div className="text-xs font-semibold text-blue-400 mb-1">
                        Understanding
                      </div>
                      <div className="text-xs text-muted-foreground italic">
                        "{msg.plan.query_understanding}"
                      </div>
                    </div>

                    {/* Thinking */}
                    {msg.plan.thinking &&
                      (showMode === "both" || showMode === "thinking") && (
                        <div className="p-3 bg-purple-500/10 border border-purple-500/30 rounded-md">
                          <div className="flex items-center gap-2 text-xs font-semibold text-purple-400 mb-2">
                            <Brain size={14} />
                            <span>Thinking</span>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {msg.plan.thinking}
                          </div>
                        </div>
                      )}

                    {/* Doing (Execution Steps) */}
                    {(showMode === "both" || showMode === "doing") && (
                      <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-md">
                        <div className="flex items-center gap-2 text-xs font-semibold text-green-400 mb-2">
                          <Zap size={14} />
                          <span>Doing</span>
                        </div>
                        <div className="space-y-2">
                          {msg.plan.steps.map((step, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-2 text-xs"
                            >
                              <CheckCircle2
                                size={14}
                                className="mt-0.5 text-green-500 flex-shrink-0"
                              />
                              <div>
                                <span className="font-medium">
                                  Step {step.step_number}:
                                </span>{" "}
                                {step.description}
                                {step.reasoning && (
                                  <div className="text-muted-foreground ml-4 mt-0.5">
                                    ↳ {step.reasoning}
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                        {msg.plan.requires_visualization && (
                          <div className="mt-2 text-xs text-green-400 flex items-center gap-1">
                            <BarChart2 size={12} />
                            <span>
                              Visualization:{" "}
                              {msg.plan.visualization_type || "auto"}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Result */}
                <div className="prose prose-invert max-w-none text-sm whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </div>

                {/* Visualization */}
                {msg.visualization && (
                  <div className="mt-4 w-full">
                    <ChartRenderer
                      data={msg.visualization.plotly_json}
                      title={msg.visualization.title}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start w-full">
            <div className="bg-muted text-foreground rounded-lg px-4 py-3 mr-12 flex items-center gap-3">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Analyzing data...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-background/80 backdrop-blur-sm border-t border-border sticky bottom-0">
        {/* Controls Row */}
        <div className="flex items-center gap-3 mb-3 max-w-4xl mx-auto">
          {/* Model Selector */}
          <div className="flex items-center gap-2 flex-1">
            <Sparkles className="w-4 h-4 text-primary flex-shrink-0" />
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="flex-1 px-3 py-2 text-sm bg-secondary border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
              disabled={isLoading}
            >
              {GEMINI_MODELS.map((model) => (
                <option key={model.value} value={model.value}>
                  {model.label} - {model.description}
                </option>
              ))}
            </select>
          </div>

          {/* Show Mode Selector */}
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-primary flex-shrink-0" />
            <select
              value={showMode}
              onChange={(e) =>
                setShowMode(e.target.value as "both" | "thinking" | "doing")
              }
              className="px-3 py-2 text-sm bg-secondary border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
              disabled={isLoading}
            >
              <option value="both">🧠 + ⚡ Both</option>
              <option value="thinking">🧠 Thinking Only</option>
              <option value="doing">⚡ Doing Only</option>
            </select>
          </div>
        </div>

        <form
          onSubmit={handleSend}
          className="relative flex items-center gap-2 max-w-4xl mx-auto"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your data..."
            className="pr-12 py-6 text-base bg-secondary border-transparent focus:border-ring"
            disabled={isLoading}
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 h-8 w-8"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
