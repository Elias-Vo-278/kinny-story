"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { books, type Book } from "@/lib/books";
type Library = {
    saved: string[];
    progress: Record<string, number>;
    name: string;
};
const initial: Library = { saved: [], progress: {}, name: '' };
const genres = ['All stories', 'Fantasy', 'Fiction', 'Romance', 'Mystery', 'Sci-fi', 'Adventure'];
function Cover({ book, large = false }: {
    book: Book;
    large?: boolean;
}) {
    return <div className={`cover ${large ? 'cover-large' : ''}`} style={{ background: book.color, color: book.accent }}><span className="cover-edition">KINNY ORIGINALS</span><span className="cover-symbol" aria-hidden="true">{book.symbol}</span><strong>{book.title}</strong><span className="cover-author">{book.author}</span></div>;
}
export default function Home() {
    const [library, setLibrary] = useState<Library>(initial);
    const [ready, setReady] = useState(false);
    const [query, setQuery] = useState('');
    const [genre, setGenre] = useState('All stories');
    const [view, setView] = useState('Discover');
    const [reader, setReader] = useState<Book | null>(null);
    const [chapter, setChapter] = useState(0);
    const [fontSize, setFontSize] = useState(20);
    const [night, setNight] = useState(false);
    const [login, setLogin] = useState(false);
    const [storageError, setStorageError] = useState('');
    const dialogRef = useRef<HTMLDialogElement>(null);
    const loginRef = useRef<HTMLDialogElement>(null);
    const lastFocus = useRef<HTMLElement | null>(null);
    useEffect(() => {
        try {
            const value = JSON.parse(localStorage.getItem('kinny-library') || 'null');
            if (value && Array.isArray(value.saved) && value.saved.every((id: unknown) => typeof id === 'string') && value.progress && typeof value.progress === 'object' && typeof value.name === 'string')
                setLibrary({ ...value, progress: Object.fromEntries(Object.entries(value.progress).filter(([id, index]) => books.some(book => book.id === id) && typeof index === "number" && Number.isInteger(index) && index >= 0)) });
        }
        catch {
            setStorageError('Your previous library could not be loaded. You can still explore and read.');
        }
        setReady(true);
    }, []);
    useEffect(() => { if (ready) {
        try {
            localStorage.setItem('kinny-library', JSON.stringify(library));
        }
        catch {
            setStorageError('Browser storage is unavailable. Changes will last for this visit only.');
        }
    } }, [library, ready]);
    useEffect(() => { if (reader) {
        dialogRef.current?.showModal();
    }
    else {
        dialogRef.current?.close();
    } }, [reader]);
    useEffect(() => { if (login)
        loginRef.current?.showModal();
    else
        loginRef.current?.close(); }, [login]);
    function openBook(book: Book) { lastFocus.current = document.activeElement as HTMLElement; setChapter(Math.max(0, Math.min(book.chapters.length - 1, library.progress[book.id] || 0))); setReader(book); }
    function closeBook() { setReader(null); lastFocus.current?.focus(); }
    function moveChapter(index: number) { if (!reader)
        return; setChapter(index); setLibrary(current => ({ ...current, progress: { ...current.progress, [reader.id]: index } })); document.querySelector('.reader-body')?.scrollTo(0, 0); }
    function save(id: string) { setLibrary(current => ({ ...current, saved: current.saved.includes(id) ? current.saved.filter(item => item !== id) : [...current.saved, id] })); }
    const visible = books.filter(book => (genre === 'All stories' || book.genre === genre) && `${book.title} ${book.author}`.toLowerCase().includes(query.toLowerCase()) && (view !== 'My library' || library.saved.includes(book.id)));
    const featured = books[0];
    const continuing = books.find(book => Object.hasOwn(library.progress, book.id));
    return <>
    <header className="header"><Link className="brand" href="/" aria-label="Kinny Story home"><span className="brand-icon">k.</span>kinny<span className="brand-story">story</span></Link><nav aria-label="Main navigation">{['Discover', 'My library'].map(item => <button key={item} className={view === item ? 'nav-active' : ''} onClick={() => setView(item)}>{item}</button>)}</nav><button className="account-button" onClick={() => setLogin(true)}>{library.name ? `Hi, ${library.name}` : 'Join the story'} <span aria-hidden="true">↗</span></button></header>
    <main className="main"><div className="intro"><div><p className="eyebrow">A LITTLE ESCAPE, A GREAT STORY</p><h1>{view === 'My library' ? 'Your next chapter is waiting.' : <>Find a story.<br />Stay for a <em>while.</em></>}</h1><p className="intro-copy">A quiet corner for curious minds. Discover novels, find your<br className="desktop-break"/> next favorite, and get a little lost in the pages.</p></div><div className="intro-note"><span aria-hidden="true">✳</span><p>For the love<br />of getting lost.</p><small>ONE CHAPTER AT A TIME</small></div></div>
    {storageError && <p role="status" className="notice">{storageError}</p>}
    {view === 'Discover' && <section className="featured" aria-label="Featured story"><div className="feature-copy"><p className="eyebrow">THE EDITOR’S PICK <span className="tiny-line"/></p><span className="genre-label">FANTASY · 2 SAMPLE CHAPTERS</span><h2>The Last Light</h2><p className="feature-author">by Elena Rivers</p><p>{featured.description}</p><button className="primary-button" onClick={() => openBook(featured)}>Start reading <span aria-hidden="true">→</span></button><span className="feature-footnote">A new world is just a page away.</span></div><div className="feature-art"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><span className="art-star star-one">✦</span><span className="art-star star-two">✧</span><Cover book={featured} large/><span className="art-caption">SOME LIGHTS NEVER GO OUT.</span></div></section>}
    {continuing && view === 'Discover' && <button className="continue-bar" onClick={() => openBook(continuing)}><span>↳ &nbsp; Pick up where you left off</span><strong>{continuing.title}</strong><span>Chapter {(library.progress[continuing.id] || 0) + 1} &nbsp; →</span></button>}
    <section className="catalog" aria-labelledby="catalog-title"><div className="section-heading"><div><p className="eyebrow">YOUR NEXT GOOD READ</p><h2 id="catalog-title">{view === 'My library' ? 'Your personal bookshelf' : 'Explore the bookshelf'}<span className="count">{visible.length}</span></h2></div><label className="search"><span aria-hidden="true">⌕</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search stories or authors" aria-label="Search stories or authors"/>{query && <button onClick={() => setQuery('')} aria-label="Clear search">×</button>}</label></div><div className="filters" aria-label="Filter stories by genre">{genres.map(item => <button key={item} aria-pressed={genre === item} className={genre === item ? 'selected' : ''} onClick={() => setGenre(item)}>{item}</button>)}</div><div className="books-grid">{visible.map(book => <article className="book-card" key={book.id}><div className="book-art"><button className="cover-button" onClick={() => openBook(book)} aria-label={`Read ${book.title}`}><Cover book={book}/></button><button className={`save-button ${library.saved.includes(book.id) ? 'saved' : ''}`} aria-pressed={library.saved.includes(book.id)} aria-label={`${library.saved.includes(book.id) ? 'Unsave' : 'Save'} ${book.title}`} onClick={() => save(book.id)}>{library.saved.includes(book.id) ? '✓' : '+'}</button></div><div className="book-meta"><span>{book.genre}</span><span>Original story</span></div><h3><button onClick={() => openBook(book)}>{book.title}</button></h3><p>{book.author}</p></article>)}</div>{visible.length === 0 && <div className="empty"><h3>{view === 'My library' && !query ? 'Make room for a good story.' : 'No stories found.'}</h3><p>{view === 'My library' ? 'Save a book with the + button to add it to your shelf.' : 'Try another title, author, or genre.'}</p><button className="text-button" onClick={() => { setQuery(''); setGenre('All stories'); setView('Discover'); }}>Explore all stories →</button></div>}</section>
    <section className="closing"><span aria-hidden="true">❧</span><p>Between the first page and the last,<br /><em>find a little something of yourself.</em></p><small>WELCOME TO KINNY STORY</small></section></main><footer><Link className="brand" href="/">kinny<span className="brand-story">story</span></Link><p>A home for stories. A place for you.</p><span>© {new Date().getFullYear()} Kinny Story</span></footer>
    <dialog ref={dialogRef} aria-label="Story reader" className={`reader ${night ? 'night' : ''}`} onCancel={closeBook} onClose={() => { if (reader)
        closeBook(); }}><div className="reader-toolbar"><span>{reader?.title}</span><div><button aria-label="Decrease text size" disabled={fontSize <= 16} onClick={() => setFontSize(size => size - 2)}>A−</button><button aria-label="Increase text size" disabled={fontSize >= 28} onClick={() => setFontSize(size => size + 2)}>A+</button><button aria-label="Toggle reader night mode" aria-pressed={night} onClick={() => setNight(!night)}>{night ? '☀' : '☾'}</button><button aria-label="Close reader" onClick={closeBook}>×</button></div></div><div className="reader-body" style={{ fontSize }}><p className="eyebrow">ORIGINAL SAMPLE · CHAPTER {chapter + 1} OF {reader?.chapters.length}</p><h2>{reader?.chapters[chapter].title}</h2><p className="reader-byline">{reader?.title} · {reader?.author}</p>{reader?.chapters[chapter].paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}<div className="chapter-controls"><button disabled={chapter === 0} onClick={() => moveChapter(chapter - 1)}>← Previous</button><span>{chapter + 1} / {reader?.chapters.length}</span><button disabled={!reader || chapter === reader.chapters.length - 1} onClick={() => moveChapter(chapter + 1)}>Next chapter →</button></div><button className="text-button" onClick={() => { if (reader) {
        setLibrary(current => ({ ...current, progress: { ...current.progress, [reader.id]: chapter } }));
        closeBook();
    } }}>Save my place & close</button></div></dialog>
    <dialog ref={loginRef} aria-label="Local reader profile" className="login-dialog" onCancel={() => setLogin(false)} onClose={() => setLogin(false)}><button className="dialog-close" onClick={() => setLogin(false)} aria-label="Close profile">×</button><p className="eyebrow">YOUR LITTLE READING CORNER</p><h2>{library.name ? 'Welcome back.' : 'Make yourself at home.'}</h2><p>This is a local demo profile. Your bookshelf stays in this browser. Secure account sign-in and sync are not connected yet.</p><form onSubmit={event => { event.preventDefault(); const data = new FormData(event.currentTarget); setLibrary(current => ({ ...current, name: String(data.get('name')).trim() })); setLogin(false); }}><label htmlFor="name">What should we call you?</label><input id="name" name="name" defaultValue={library.name} required maxLength={30} pattern=".*\S.*" placeholder="Your name" autoComplete="given-name"/><button className="primary-button" type="submit">Save local profile →</button></form>{library.name && <button className="text-button" onClick={() => { setLibrary(current => ({ ...current, name: '' })); setLogin(false); }}>Remove local profile name</button>}</dialog>
  </>;
}
