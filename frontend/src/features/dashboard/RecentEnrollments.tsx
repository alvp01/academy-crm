import { Card, CardHeader, CardTitle } from "../../components/ui/Card";
import { Avatar } from "../../components/ui/Avatar";

interface Enrollment {
  name: string;
  course: string;
  time: string;
}

const mockEnrollments: Enrollment[] = [
  { name: "Sarah Johnson", course: "Piano Advanced", time: "2 hours ago" },
  { name: "Michael Chen", course: "Guitar Basics", time: "4 hours ago" },
  { name: "Emma Wilson", course: "Violin Intermediate", time: "6 hours ago" },
];

export function RecentEnrollments() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Enrollments</CardTitle>
      </CardHeader>
      <div className="space-y-4">
        {mockEnrollments.map((item, i) => (
          <div key={i} className="flex items-center gap-4 p-3 bg-surface-background rounded-xl">
            <Avatar name={item.name} size="md" />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-text truncate">{item.name}</p>
              <p className="text-sm text-text-light">{item.course}</p>
            </div>
            <span className="text-xs text-text-light whitespace-nowrap">{item.time}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
