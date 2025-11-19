import React from 'react';
import { Navbar } from '../Navbar';
import { Button } from '../ui/button';
import { useNavigate } from 'react-router-dom';

export const AboutPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="h-screen flex flex-col bg-background">
      <Navbar sessionId={null} onClearSession={() => {}} isStreaming={false} loading={false} />
      <div className="flex-1 w-full select-none">
        <div className="grid grid-cols-[1fr_3fr] border-b border-border w-full h-full">
          <div>
            <div className="grid grid-rows-[1fr_2fr] border-r border-border h-full">
              <div className="p-12 text-2xl border-b border-border h-full flex items-center justify-center leading-snug text-foreground">
                <div className="max-w-md">
                  <p>
                    About CLERK, an <span className="font-bold text-primary">Open Source AI Agent</span> for Analyzing Court Decisions with Ease
                  </p>
                </div>
              </div>
              <div className="diagonal-lines" />
            </div>
          </div>
          <div className="flex items-start justify-center p-12 bg-blue-animation overflow-y-auto">
            <div className="max-w-2xl prose prose-invert m-auto">
              <section>
                <h2 className="text-xl font-semibold tracking-wide uppercase text-foreground">Origin</h2>
                <p>
                  CLERK began as a focused private international law assistant built during the development of the{' '}
                  <a href="https://cold.global" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                    cold.global
                  </a>{' '}
                  platform. The original prototype is still live at{' '}
                  <a
                    href="https://case-analyzer.cold.global"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    case-analyzer.cold.global
                  </a>{' '}
                  .
                </p>
              </section>
              <section>
                <h2 className="text-xl font-semibold tracking-wide uppercase text-foreground">Future</h2>
                <p>
                  We're evolving into a modular ecosystem: pluggable agents, MCP integrations, tool orchestration, and structured legal workflows. A foundation designed for community extension, not a black box. We aim to automate the analytical backbone of legal processes, converting costly manual routines into repeatable, high-signal reasoning steps. CLERK is a platform for capturing best practices and codifying reliable automation patterns.
                </p>
              </section>
              <section>
                <h2 className="text-xl font-semibold tracking-wide uppercase text-foreground">Why</h2>
                <p>
                  Openness drives trust. Transparent logic enables auditability, reliability, and collaboration. Legal AI should be inspectable, improvable, and secure by design.
                </p>
                <p>
                  Find out more:{' '}
                  <a
                    href="https://github.com/simonweigold/legal-case-analyzer"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    github.com/simonweigold/legal-case-analyzer
                  </a>
                  .
                </p>
              </section>
            </div>
          </div>
        </div>
      </div>
      <div className="grid place-items-center p-4 text-xs text-muted-foreground">
        © {new Date().getFullYear()} CLERK
      </div>
    </div>
  );
};
