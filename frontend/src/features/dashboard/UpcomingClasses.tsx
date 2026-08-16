import { Card, CardHeader, CardTitle } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";

interface Class {
  name: string;
  time: string;
  students: number;
  room: string;
}

const mockClasses: Class[] = [
  { name: "Piano Advanced", time: "10:00 AM", students: 12, room: "Room A" },
  { name: "Guitar Basics", time: "11:30 AM", students: 8, room: "Room B" },
  { name: "Violin Intermediate", time: "2:00 PM", students: 10, room: "Room C" },
];

export function UpcomingClasses() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Upcoming Classes</CardTitle>
      </CardHeader>
      <div className="space-y-4">
        {mockClasses.map((item, i) => (
          <div key={i} className="flex items-center gap-4 p-3 bg-surface-background rounded-xl">
            <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center text-brand-700 font-medium text-sm">
              {item.time.split(" ")[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-text truncate">{item.name}</p>
              <p className="text-sm text-text-light">{item.students} students · {item.room}</p>
            </div>
            <Badge variant="success">{item.time}</Badge>
          </div>
        ))}
      </div>
    </Card>
  );
}
