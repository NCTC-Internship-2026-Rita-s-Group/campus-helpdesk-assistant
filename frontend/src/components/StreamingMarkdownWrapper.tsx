import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";

interface StreamingProps {
  text: string;
  speed?: number; // Time interval delay in milliseconds per word token block
}

export function StreamingMarkdownWrapper({ text, speed = 25 }: StreamingProps) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    const wordTokens = text.split(" ");
    let currentWordIndex = 0;
    setDisplayedText(""); // Clear viewport baseline on fresh triggers

    const streamingTimer = setInterval(() => {
      if (currentWordIndex < wordTokens.length) {
        setDisplayedText((prev) => (prev ? prev + " " : "") + wordTokens[currentWordIndex]);
        currentWordIndex++;
      } else {
        clearInterval(streamingTimer);
      }
    }, speed);

    return () => clearInterval(streamingTimer);
  }, [text, speed]);

  const parseBoldFormatting = (rawString: string) => {
    const segments = rawString.split(/(\*\*.*?\*\*)/g);
    return segments.map((chunk, idx) => {
      if (chunk.startsWith("**") && chunk.endsWith("**")) {
        return (
          <strong key={idx} className="font-bold text-[color:var(--gold)] select-text">
            {chunk.slice(2, -2)}
          </strong>
        );
      }
      return chunk;
    });
  };

  const codeLines = displayedText.split("\n");

  return (
    <div className="space-y-2.5 text-left font-sans text-[13.5px] tracking-normal text-slate-200 leading-relaxed transition-all duration-300">
      {codeLines.map((lineStr, lineIdx) => {
        const leadingWhitespaceCount = lineStr.match(/^(\s*)/)?.[0].length || 0;
        const structuralRow = lineStr.trim();

        if (!structuralRow) return <div key={lineIdx} className="h-1" />;

        // 1. Structural Block Main Headers
        if (structuralRow.startsWith("###")) {
          return (
            <h3
              key={lineIdx}
              className="font-display text-sm font-bold uppercase tracking-wider text-slate-100 mt-5 mb-2.5 flex items-center gap-2 border-b border-white/5 pb-1 select-none"
            >
              <Sparkles className="h-3.5 w-3.5 text-[color:var(--gold)] shrink-0 animate-pulse" />
              {parseBoldFormatting(structuralRow.replace(/^###\s*/, ""))}
            </h3>
          );
        }

        // 2. Structural Secondary Section Headers
        if (structuralRow.startsWith("##")) {
          return (
            <h2
              key={lineIdx}
              className="font-display text-base font-bold text-white mt-4 mb-2 tracking-tight"
            >
              {parseBoldFormatting(structuralRow.replace(/^##\s*/, ""))}
            </h2>
          );
        }

        // 3. Multi-tier Child Nested Bullets
        if (leadingWhitespaceCount >= 2 || structuralRow.startsWith("+")) {
          const strippedPayload = structuralRow.replace(/^[\*\-\+]\s*/, "");
          return (
            <div key={lineIdx} className="flex items-start gap-2.5 pl-6 my-1 animate-fade-in">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-slate-400" />
              <p className="flex-1 text-slate-300 text-xs font-medium leading-relaxed">
                {parseBoldFormatting(strippedPayload)}
              </p>
            </div>
          );
        }

        // 4. Primary Root Bullet Indices
        if (structuralRow.startsWith("*") || structuralRow.startsWith("-")) {
          const strippedPayload = structuralRow.replace(/^[\*\-]\s*/, "");
          return (
            <div key={lineIdx} className="flex items-start gap-3 pl-1 mt-3 mb-1 animate-fade-in">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-sm bg-[color:var(--gold)]/80 shadow-[0_0_8px_var(--gold)]" />
              <div className="flex-1 font-semibold text-slate-100 leading-relaxed tracking-wide">
                {parseBoldFormatting(strippedPayload)}
              </div>
            </div>
          );
        }

        // 5. Normal Standard Copy Blocks
        return (
          <p
            key={lineIdx}
            className="text-slate-300 font-normal pl-0.5 leading-relaxed transition-all duration-200"
          >
            {parseBoldFormatting(lineStr)}
          </p>
        );
      })}
    </div>
  );
}
