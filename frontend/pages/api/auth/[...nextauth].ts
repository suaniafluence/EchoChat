import NextAuth, { NextAuthOptions } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

// Liste des emails autorisés (admins)
const ALLOWED_EMAILS = process.env.ALLOWED_ADMIN_EMAILS?.split(',') || [];

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
    }),
  ],
  callbacks: {
    async signIn({ user }) {
      // Si ALLOWED_ADMIN_EMAILS est vide, autoriser tous les utilisateurs Google
      if (ALLOWED_EMAILS.length === 0) {
        return true;
      }
      // Sinon, vérifier si l'email est dans la liste
      return ALLOWED_EMAILS.includes(user.email || '');
    },
    async session({ session }) {
      return session;
    },
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
  secret: process.env.NEXTAUTH_SECRET,
};

export default NextAuth(authOptions);
