import { Header } from "./components/Header";
import { FileUploadSidebar } from "./components/FileUploadSidebar";
import { AnalysisContent } from "./components/AnalysisContent";
import { ConversationsSidebar } from "./components/ConversationsSidebar";

export default function App() {
  return (
    <div className="h-screen flex flex-col bg-background">
      <Header />
      
      <div className="flex-1 flex overflow-hidden">
        <FileUploadSidebar />
        <AnalysisContent />
        <ConversationsSidebar />
      </div>
    </div>
  );
}