import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';

export default function AuthError() {
  const router = useRouter();
  const { error } = router.query;

  const errorMessages: Record<string, string> = {
    AccessDenied: "Accès refusé. Votre email n'est pas autorisé à accéder à l'administration.",
    Configuration: "Erreur de configuration du serveur d'authentification.",
    Verification: "Le lien de vérification a expiré ou a déjà été utilisé.",
    Default: "Une erreur s'est produite lors de l'authentification.",
  };

  const message = errorMessages[error as string] || errorMessages.Default;

  return (
    <>
      <Head>
        <title>Erreur - EchoChat Admin</title>
      </Head>
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg text-center">
          <div className="text-red-500">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Erreur d'authentification</h2>
          <p className="text-gray-600">{message}</p>
          <Link
            href="/auth/signin"
            className="inline-block mt-4 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            Réessayer
          </Link>
        </div>
      </div>
    </>
  );
}
