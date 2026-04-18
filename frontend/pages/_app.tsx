import type { AppProps } from 'next/app';
import Head from 'next/head';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
    return (
        <>
            <Head>
                <title>eCourts — Court Automation Suite | Ministry of Law &amp; Justice</title>
                <meta name="description" content="Official Court Automation Suite — AI-powered Indian court case tracking, cause list monitoring, and legal analytics. Ministry of Law & Justice, Govt. of India." />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="icon" type="image/png" href="/emblem.png" />
                <link rel="shortcut icon" type="image/png" href="/emblem.png" />
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap" rel="stylesheet" />
            </Head>
            <Component {...pageProps} />
        </>
    );
}
