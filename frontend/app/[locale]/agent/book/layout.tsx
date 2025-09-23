import ProtectedRoute from '@/components/ProtectedRoute';

export default function AgentBookLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute requiredRole="agent">
      {children}
    </ProtectedRoute>
  );
}
