import React from 'react';
import { Navbar } from '../Navbar';

// Super minimal landing page: just the Navbar inside an app-like container.
// Matches the original App header styling and leaves the rest of the screen blank.
export const LandingPage: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-background">
      <Navbar sessionId={null} onClearSession={() => {}} isStreaming={false} loading={false} />
      <div className="flex-1 flex items-center justify-center text-muted-foreground select-none">
        {/*Grid with two columns and grey borders for every grid field. The first column is 1/3 wide. The second 2/3*/}
        <div className="grid grid-cols-[1fr_3fr_1fr] border-b border-border w-full h-full">
            <div className="">
                <div className="grid grid-rows-[1fr_2fr] border-r border-border h-full">
                  <div className="p-12 text-2xl border-b border-border h-full flex items-center justify-center leading-snug">
                    Welcome to CAUSA AI, an agentic AI web app for analyzing court decisions with ease
                  </div>
                    <div className="p-2 bg-muted/30 diagonal-lines">Column 1 Row 2 Shaded</div>
                </div>
            </div>
            <div className="">
                Placeholder
            </div>
            <div className="grid grid-rows-[2fr_1fr] border-l border-border h-full">
                <div className="p-12 text-2xl h-full flex items-center justify-center border-b border-border leading-snug">
                    Start by uploading your case or learn more about this project by clicking here
                </div>
                <div className="bg-muted/30  diagonal-lines">
                </div>
            </div>
        </div>
      </div>
      <div className="grid place-items-center p-4 text-xs text-muted-foreground">
        © {new Date().getFullYear()} CAUSA AI
      </div>
    </div>
  );
};
