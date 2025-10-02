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
        <div className="grid grid-cols-2 border border-gray-200 w-full h-full">
            <div className="">
                <div className="grid grid-rows-2 border border-gray-200 h-full">
                    <div className="border border-gray-200">Column 1 Row 1</div>
                    <div className="border border-gray-200">Column 1 Row 2</div>
                </div>
            </div>
            <div className="">
                <div className="grid grid-rows-2 border border-gray-200 h-full">
                    <div className="border border-gray-200">Column 2 Row 1</div>
                    <div className="border border-gray-200">Column 2 Row 2</div>
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
