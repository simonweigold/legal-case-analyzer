import { Menu } from "lucide-react";
import { Button } from "./ui/button";

export function Header() {
  return (
    <header className="border-b border-border bg-background px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
              <div className="w-2 h-2 bg-white rounded-full"></div>
            </div>
            <h1 className="tracking-wider">CAUSA AI</h1>
          </div>
        </div>
      </div>
    </header>
  );
}