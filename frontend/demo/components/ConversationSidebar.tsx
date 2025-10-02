import { useState } from "react";
import { X, Search, MessageCircle, User } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}

export function ConversationsSidebar() {
  const [isOpen, setIsOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const conversations: Conversation[] = [
    {
      id: "1",
      title: "Case Analysis #1",
      lastMessage:
        "Analysis completed for contract dispute case",
      timestamp: "2 hours ago",
    },
    {
      id: "2",
      title: "Legal Research",
      lastMessage: "Found 12 relevant precedents",
      timestamp: "1 day ago",
    },
    {
      id: "3",
      title: "Document Review",
      lastMessage: "Reviewed 45 pages of evidence",
      timestamp: "2 days ago",
    },
  ];

  const filteredConversations = conversations.filter(
    (conv) =>
      conv.title
        .toLowerCase()
        .includes(searchQuery.toLowerCase()) ||
      conv.lastMessage
        .toLowerCase()
        .includes(searchQuery.toLowerCase()),
  );

  if (!isOpen) {
    return (
      <Button
        variant="outline"
        size="sm"
        className="fixed top-4 right-4 z-10"
        onClick={() => setIsOpen(true)}
      >
        <MessageCircle className="w-4 h-4" />
      </Button>
    );
  }

  return (
    <div className="w-80 border-l border-border bg-background flex flex-col">
      <div className="p-4 border-b border-border diagonal-lines">
        <div className="flex items-center justify-between mb-4">
          <h3>Conversations</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(false)}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search Conversations"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {filteredConversations.length > 0 ? (
            filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                className="p-3 rounded-lg border border-border hover:bg-muted/50 cursor-pointer transition-colors"
              >
                <h4 className="mb-1 truncate">
                  {conversation.title}
                </h4>
                <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                  {conversation.lastMessage}
                </p>
                <p className="text-xs text-muted-foreground">
                  {conversation.timestamp}
                </p>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              No conversations found
            </p>
          )}
        </div>
      </ScrollArea>

      <div className="border-t border-border p-4 bg-muted/30 diagonal-lines">
        <div className="flex items-center gap-3 p-3 rounded-lg bg-background">
          <div className="w-8 h-8 rounded-full bg-background flex items-center justify-center">
            <User className="w-4 h-4" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm truncate">admin@admin.com</p>
          </div>
          <Button variant="ghost" size="sm">
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}