export type Book = {
    id: string;
    title: string;
    author: string;
    genre: string;
    color: string;
    accent: string;
    symbol: string;
    description: string;
    chapters: {
        title: string;
        paragraphs: string[];
    }[];
};
const stories = [
    ['the-last-light', 'The Last Light', 'Elena Rivers', 'Fantasy', '#253d39', '#e8bc75', '☾', 'In a city where stars have forgotten how to shine, one mapmaker discovers a light that could change everything.'],
    ['a-season-of-small-things', 'A Season of Small Things', 'Noah Bennett', 'Fiction', '#b86748', '#ffe5ba', '✿', 'An unexpected inheritance brings a restless traveler to a seaside village, and to the quiet wonder of starting again.'],
    ['the-quiet-orbit', 'The Quiet Orbit', 'Mira Chen', 'Sci-fi', '#253754', '#b8c9df', '◎', 'Alone above a sleeping planet, an archivist receives a message that should have arrived a century ago.'],
    ['letters-from-june', 'Letters from June', 'Isabel Hart', 'Romance', '#a67875', '#ffdfc8', '❦', 'Two strangers. One forgotten address. A summer of letters that will bring them closer than they ever imagined.'],
    ['beneath-the-pines', 'Beneath the Pines', 'Oliver Reed', 'Mystery', '#454c36', '#d2d3a3', '♧', 'When the old forest gives up a long-lost journal, a small town must confront the story it chose to forget.'],
    ['where-rivers-meet', 'Where Rivers Meet', 'Amara Ellis', 'Adventure', '#526b76', '#e6d4aa', '≈', 'A journey beyond the familiar follows two siblings searching for the place their mother once called home.'],
];
export const books: Book[] = stories.map(([id, title, author, genre, color, accent, symbol, description]) => ({ id, title, author, genre, color, accent, symbol, description, chapters: [
        { title: 'An unexpected beginning', paragraphs: [
                'The morning arrived quietly, slipping through the curtains before the town had stirred. On the windowsill, a folded letter waited beside a cup of tea that had long since gone cold.',
                'For three days, Rowan had pretended not to see it. There were ordinary things to do: shelves to dust, a loose hinge to mend, bread to fetch from the woman at the corner. An unopened letter could wait. An entire life, carefully arranged, could not.',
                'But that morning the light fell differently. It caught the handwriting on the envelope, the familiar curl of a name, and something in the room seemed to hold its breath.',
                'Outside, someone laughed. A bicycle rattled over the stones. The world carried on with its small, insistent music. Rowan reached for the letter.',
                'There was no greeting inside. Only a map, drawn in blue ink, and a single sentence: If you still remember the way, come before the last light.',
                'The map showed a road that did not exist anymore. Rowan knew this because, twenty years before, they had watched the river take it. And yet there it was, every bend and crossing, every impossible mile.',
                'For the first time in a very long while, the day ahead was no longer certain. Rowan put on a coat, slipped the map into a pocket, and opened the door.'
            ] },
        { title: 'The road beyond', paragraphs: [
                'Beyond the last house, the path narrowed to a thread between the fields. The air smelled of rain and turned earth. Rowan walked until the sounds of the town were replaced by the wind.',
                'At the old bridge, a stranger sat with a notebook on their knees. They looked up as though they had been expecting company.',
                '“You have the map,” the stranger said. It was a statement, not a question. Rowan kept one hand in the coat pocket and waited.',
                '“There are other roads,” the stranger continued. “Most people stop looking after they find the first one.” They closed the notebook and stood, leaving room on the narrow path.',
                'The river was low. Where there should have been only water, pale stones traced a crossing toward the trees. Rowan unfolded the letter once more. In the afternoon light, a second line appeared beneath the first.',
                'This time, you do not have to go alone.',
                'Rowan looked toward the forest, then back at the stranger. Together, without another word, they stepped onto the stones. The next chapter was waiting to be lived.'
            ] }
    ] }));
