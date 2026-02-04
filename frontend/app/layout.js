import './globals.css'
import { AuthProvider } from '@/lib/auth'

export const metadata = {
  title: 'Gmail AI Assistant',
  description: 'AI-powered Gmail automation assistant',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
