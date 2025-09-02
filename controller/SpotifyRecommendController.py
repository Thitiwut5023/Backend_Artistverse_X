from flask import jsonify, request
import spotipy
import os
from dotenv import load_dotenv
import random
import re

load_dotenv()

class SpotifyRecommendController:
    def __init__(self):
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        
        # Audio features estimation data
        self.genre_tempo_map = {
            'pop': {'min': 120, 'max': 140, 'mode': 'Major'},
            'rock': {'min': 120, 'max': 160, 'mode': 'Minor'},
            'hip-hop': {'min': 70, 'max': 140, 'mode': 'Minor'},
            'rap': {'min': 70, 'max': 140, 'mode': 'Minor'},
            'electronic': {'min': 120, 'max': 180, 'mode': 'Major'},
            'dance': {'min': 120, 'max': 140, 'mode': 'Major'},
            'indie': {'min': 100, 'max': 130, 'mode': 'Major'},
            'folk': {'min': 80, 'max': 120, 'mode': 'Major'},
            'country': {'min': 100, 'max': 140, 'mode': 'Major'},
            'jazz': {'min': 60, 'max': 200, 'mode': 'Major'},
            'blues': {'min': 60, 'max': 120, 'mode': 'Minor'},
            'reggae': {'min': 60, 'max': 90, 'mode': 'Major'},
            'punk': {'min': 150, 'max': 200, 'mode': 'Minor'},
            'metal': {'min': 120, 'max': 200, 'mode': 'Minor'},
            'classical': {'min': 60, 'max': 200, 'mode': 'Major'},
            'alternative': {'min': 100, 'max': 140, 'mode': 'Minor'},
            'r&b': {'min': 70, 'max': 130, 'mode': 'Major'},
            'soul': {'min': 70, 'max': 130, 'mode': 'Major'},
            'funk': {'min': 100, 'max': 130, 'mode': 'Major'},
            'ambient': {'min': 60, 'max': 100, 'mode': 'Major'},
        }
        
        self.artist_genre_map = {
            'taylor swift': 'pop',
            'ed sheeran': 'pop',
            'drake': 'hip-hop',
            'ariana grande': 'pop',
            'post malone': 'hip-hop',
            'the weeknd': 'r&b',
            'dua lipa': 'pop',
            'olivia rodrigo': 'pop',
            'harry styles': 'pop',
            'billie eilish': 'alternative',
            'arctic monkeys': 'indie',
            'the walters': 'indie',
            'little john': 'hip-hop',
            'ten': 'pop',
            'arafat': 'hip-hop',
            'nct dream': 'pop',
        }
    def get_recommendations(self):
        """Get music recommendations from Spotify API"""
        try:
            # Validate access token
            auth_result = self._validate_access_token()
            if auth_result['error']:
                return jsonify({
                    'success': False,
                    'error': auth_result['error']
                }), auth_result['status_code']
            
            sp = auth_result['spotify_client']
            
            # Get recommendations from multiple sources
            recommendations = self._gather_recommendations(sp)
            
            # Process and return final recommendations
            final_recommendations = self._process_recommendations(recommendations)
            
            return jsonify({
                'success': True,
                'recommendations': final_recommendations,
                'total': len(final_recommendations),
                'source': 'mixed' if len(final_recommendations) > 0 else 'fallback'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def _validate_access_token(self):
        """Validate access token and return Spotify client"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {
                'error': 'Access token is required',
                'status_code': 401,
                'spotify_client': None
            }

        access_token = auth_header.split(' ')[1]
        sp = spotipy.Spotify(auth=access_token)
        
        # Test token validity
        try:
            sp.current_user()
            return {
                'error': None,
                'status_code': 200,
                'spotify_client': sp
            }
        except Exception:
            return {
                'error': 'Invalid or expired access token',
                'status_code': 401,
                'spotify_client': None
            }
    
    def _gather_recommendations(self, sp):
        """Gather recommendations from multiple sources"""
        recommendations = []
        
        # Try to get user's top tracks first
        user_tracks = self._get_user_top_tracks(sp)
        recommendations.extend(user_tracks)
        
        # If we don't have enough tracks, get popular tracks
        if len(recommendations) < 8:
            popular_tracks = self._get_popular_tracks(sp, 12 - len(recommendations))
            recommendations.extend(popular_tracks)
        
        # If still not enough, try alternative search
        if len(recommendations) < 8:
            alternative_tracks = self._get_featured_playlist_tracks(sp, 12 - len(recommendations))
            recommendations.extend(alternative_tracks)
        
        return recommendations
    def _get_user_top_tracks(self, sp):
        """Get user's top tracks from multiple time ranges"""
        tracks = []
        time_ranges = ['short_term', 'medium_term', 'long_term']
        
        for time_range in time_ranges:
            if len(tracks) >= 6:
                break
                
            try:
                print(f"Trying to get user top tracks for {time_range}...")
                user_top_tracks = sp.current_user_top_tracks(
                    limit=6 - len(tracks), 
                    time_range=time_range
                )
                
                new_tracks = user_top_tracks['items']
                print(f"Got {len(new_tracks)} user top tracks for {time_range}")
                
                for track in new_tracks:
                    if len(tracks) >= 6:
                        break
                    tracks.append(self._format_track(track))
                        
            except Exception as e:
                print(f"Could not get user top tracks for {time_range}: {e}")
                continue
        
        # If still no tracks, try getting recently played tracks
        if len(tracks) == 0:
            try:
                print("Trying recently played tracks...")
                recent_tracks = sp.current_user_recently_played(limit=6)
                for item in recent_tracks['items']:
                    track = item['track']
                    tracks.append(self._format_track(track))
                print(f"Got {len(recent_tracks['items'])} recently played tracks")
            except Exception as e:
                print(f"Could not get recently played tracks: {e}")
        
        print(f"Total user tracks collected: {len(tracks)}")
        return tracks
    
    def _process_recommendations(self, recommendations):
        """Process recommendations to remove duplicates and shuffle"""
        # Remove duplicates based on track ID
        seen_ids = set()
        unique_recommendations = []
        for track in recommendations:
            if track['spotify_id'] not in seen_ids:
                seen_ids.add(track['spotify_id'])
                unique_recommendations.append(track)
        
        # Shuffle and limit to 12 tracks
        random.shuffle(unique_recommendations)
        return unique_recommendations[:12]    
    def _get_popular_tracks(self, sp, limit):
        """Get popular tracks using search API"""
        tracks = []
        try:
            # Search for popular songs by different criteria
            search_queries = [
                'year:2024 OR year:2023',
                'genre:pop',
                'genre:rock',
                'genre:indie',
                'genre:hip-hop',
                'artist:Taylor Swift OR artist:Ed Sheeran OR artist:Drake'
            ]
            
            tracks_per_query = max(1, limit // len(search_queries))
            
            for query in search_queries:
                if len(tracks) >= limit:
                    break
                try:
                    results = sp.search(q=query, type='track', limit=tracks_per_query, market='US')
                    for track in results['tracks']['items']:
                        if len(tracks) >= limit:
                            break
                        if track and track['id']:  # Only require track ID, not preview_url
                            tracks.append(self._format_track(track))
                except Exception as e:
                    print(f"Error searching for tracks with query '{query}': {e}")
                    continue
                    
        except Exception as e:
            print(f"Error getting popular tracks: {e}")
        
        return tracks
    def _get_featured_playlist_tracks(self, sp, limit):
        """Get popular tracks using alternative search methods"""
        tracks = []
        
        # Use search for specific popular artists and songs
        popular_searches = [
            'track:Shape of You artist:Ed Sheeran',
            'track:Blinding Lights artist:The Weeknd',
            'track:Watermelon Sugar artist:Harry Styles',
            'track:Good 4 U artist:Olivia Rodrigo',
            'track:Levitating artist:Dua Lipa',
            'artist:Taylor Swift',
            'artist:Ariana Grande',
            'artist:Post Malone'
        ]
        
        tracks_per_search = max(1, limit // len(popular_searches))
        
        for search_term in popular_searches:
            if len(tracks) >= limit:
                break
            try:
                results = sp.search(q=search_term, type='track', limit=tracks_per_search, market='US')
                for track in results['tracks']['items']:
                    if len(tracks) >= limit:
                        break
                    if track and track['id']:
                        tracks.append(self._format_track(track))
            except Exception as e:
                print(f"Error searching for '{search_term}': {e}")
                continue
        
        return tracks
    
    def _format_track(self, track):
        """Format track data for frontend"""
        # Get artist names
        artists = [artist['name'] for artist in track['artists']]
        artist_name = ', '.join(artists)
        
        # Get album image
        image_url = None
        if track['album']['images']:
            # Get the medium-sized image (usually index 1, or fallback to largest)
            if len(track['album']['images']) > 1:
                image_url = track['album']['images'][1]['url']
            else:
                image_url = track['album']['images'][0]['url']
          # Get release year
        release_date = track['album']['release_date']
        year = release_date.split('-')[0] if release_date else 'Unknown'
        
        # Estimate genre from artist and track name
        estimated_genre = self._estimate_genre(artist_name.lower(), track['name'].lower())
        
        # Get additional track features if available
        formatted_track = {
            'id': hash(track['id']) % 100000,  # Create a more unique numeric ID from Spotify ID
            'spotify_id': track['id'],
            'name': track['name'] or 'Unknown Song',
            'artist': artist_name or 'Unknown Artist',
            'album': track['album']['name'] or 'Unknown Album',
            'image': image_url,
            'spotify_url': track['external_urls']['spotify'],
            'preview_url': track['preview_url'],            'year': year,
            'popularity': track['popularity'],
            'duration_ms': track['duration_ms'],
            # Default values for fields not available from basic track info
            'mood': 'Unknown',
            'genre': estimated_genre.title(),  # Capitalize first letter (e.g., 'pop' -> 'Pop')
            'tempo': 'Unknown',
            'style': self._create_music_style(artist_name, estimated_genre, track['popularity']),
            'instruments': self._estimate_instruments(estimated_genre),
            'keywords': self._generate_keywords(estimated_genre, track['name'], artist_name),
            'shortLyric': 'Preview not available',
            'description': f'A track by {artist_name} from the album {track["album"]["name"]}.'
        }
        
        return formatted_track        
    def get_track_features(self):
        """Get detailed audio features for tracks using estimation algorithms"""
        try:
            # Get access token from request headers
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'success': False,
                    'error': 'Access token is required'
                }), 401

            access_token = auth_header.split(' ')[1]
            data = request.get_json()
            track_ids = data.get('track_ids', [])
            
            if not track_ids:
                return jsonify({
                    'success': False,
                    'error': 'Track IDs are required'
                }), 400
            
            # Create Spotify client with access token
            sp = spotipy.Spotify(auth=access_token)
            
            formatted_features = {}
            
            # Process tracks one by one to get basic track info and estimate features
            for track_id in track_ids:
                try:
                    # Get basic track information
                    track = sp.track(track_id)
                    
                    if track:
                        # Estimate audio features from track metadata
                        estimated_features = self._estimate_audio_features(track)
                        formatted_features[track_id] = estimated_features
                    else:
                        # Return default features if no track data
                        formatted_features[track_id] = self._get_default_features()
                        
                except Exception as e:
                    print(f"Could not get track info for {track_id}: {e}")
                    # Use default features as fallback
                    formatted_features[track_id] = self._get_default_features()
            
            return jsonify({
                'success': True,
                'features': formatted_features,
                'has_detailed_features': True,
                'estimation_note': 'Audio features estimated from track metadata'
            })
            
        except Exception as e:
            print(f"Error in get_track_features: {e}")
            return jsonify({
                'success': False,
                'error': 'Unable to get track features',
                'details': str(e)
            }), 500    
        
    def _estimate_audio_features(self, track):
        """Estimate audio features from track metadata"""
        # Get artist info
        artist_name = track['artists'][0]['name'].lower() if track['artists'] else 'unknown'
        track_name = track['name'].lower() if track['name'] else 'unknown'
        popularity = track.get('popularity', 50)
        duration_ms = track.get('duration_ms', 180000)  # Default 3 minutes
        
        # Estimate genre from artist
        estimated_genre = self._estimate_genre(artist_name, track_name)
        
        # Get tempo range for genre
        tempo_info = self.genre_tempo_map.get(estimated_genre, {'min': 100, 'max': 130, 'mode': 'Major'})
        
        # Calculate estimated tempo based on duration and popularity
        tempo_base = (tempo_info['min'] + tempo_info['max']) / 2
        tempo_variation = (popularity - 50) * 0.5  # Popular songs tend to be slightly faster
        estimated_tempo = int(tempo_base + tempo_variation)
        
        # Ensure tempo stays within genre bounds
        estimated_tempo = max(tempo_info['min'], min(tempo_info['max'], estimated_tempo))
        
        # Estimate energy based on genre and popularity
        energy = self._estimate_energy(estimated_genre, popularity)
        
        # Estimate valence (happiness) based on genre and tempo
        valence = self._estimate_valence(estimated_genre, estimated_tempo)
        
        # Estimate danceability based on tempo and genre
        danceability = self._estimate_danceability(estimated_tempo, estimated_genre)
        
        # Estimate acousticness based on genre
        acousticness = self._estimate_acousticness(estimated_genre)
        
        # Estimate key and mode
        key = self._estimate_key(estimated_genre, track_name)
        mode = tempo_info['mode']
        
        # Convert valence to mood text
        mood = self._valence_to_mood(valence, energy)
        
        return {
            'tempo': f"{estimated_tempo} BPM",
            'energy': energy,
            'valence': valence,
            'danceability': danceability,
            'acousticness': acousticness,
            'key': key,
            'mode': mode,
            'mood': mood
        }

    def _estimate_genre(self, artist_name, track_name):
        """Estimate genre from artist name and track name"""
        # Check known artist mappings
        if artist_name in self.artist_genre_map:
            return self.artist_genre_map[artist_name]
        
        # Check for genre keywords in artist name or track name
        text_to_check = f"{artist_name} {track_name}".lower()
        
        genre_keywords = {
            'pop': ['pop', 'mainstream', 'chart', 'hit'],
            'rock': ['rock', 'metal', 'punk', 'alternative'],
            'hip-hop': ['hip', 'hop', 'rap', 'trap', 'drill'],
            'electronic': ['electronic', 'edm', 'techno', 'house', 'dubstep'],
            'indie': ['indie', 'independent', 'alternative'],
            'jazz': ['jazz', 'blues', 'swing'],
            'folk': ['folk', 'acoustic', 'country'],
            'r&b': ['r&b', 'soul', 'funk']
        }
        
        for genre, keywords in genre_keywords.items():
            for keyword in keywords:
                if keyword in text_to_check:
                    return genre
        
        # Default to pop for unknown
        return 'pop'

    def _estimate_energy(self, genre, popularity):
        """Estimate energy level based on genre and popularity"""
        base_energy = {
            'pop': 70, 'rock': 80, 'hip-hop': 75, 'electronic': 85,
            'indie': 60, 'jazz': 50, 'folk': 40, 'r&b': 65,
            'metal': 90, 'punk': 85, 'blues': 45, 'ambient': 25
        }
        
        energy = base_energy.get(genre, 60)
        # Adjust based on popularity (popular songs tend to be more energetic)
        energy += (popularity - 50) * 0.3
        return max(0, min(100, int(energy)))

    def _estimate_valence(self, genre, tempo):
        """Estimate valence (happiness) based on genre and tempo"""
        base_valence = {
            'pop': 70, 'rock': 45, 'hip-hop': 55, 'electronic': 65,
            'indie': 50, 'jazz': 60, 'folk': 55, 'r&b': 60,
            'metal': 35, 'punk': 40, 'blues': 30, 'ambient': 45
        }
        
        valence = base_valence.get(genre, 50)
        # Faster tempo generally means happier
        if tempo > 130:
            valence += 15
        elif tempo < 80:
            valence -= 15
            
        return max(0, min(100, int(valence)))

    def _estimate_danceability(self, tempo, genre):
        """Estimate danceability based on tempo and genre"""
        # Optimal dance tempo is around 120-140 BPM
        if 110 <= tempo <= 150:
            base_dance = 80
        elif 90 <= tempo <= 170:
            base_dance = 65
        else:
            base_dance = 40
            
        # Genre adjustments
        genre_bonus = {
            'pop': 10, 'electronic': 20, 'hip-hop': 15, 'r&b': 10,
            'rock': -10, 'folk': -20, 'jazz': -5, 'metal': -15
        }
        
        danceability = base_dance + genre_bonus.get(genre, 0)
        return max(0, min(100, int(danceability)))

    def _estimate_acousticness(self, genre):
        """Estimate acousticness based on genre"""
        base_acoustic = {
            'folk': 85, 'jazz': 70, 'blues': 65, 'indie': 45,
            'pop': 25, 'rock': 15, 'electronic': 5, 'hip-hop': 10,
            'metal': 5, 'punk': 10, 'r&b': 30, 'ambient': 60
        }
        
        return base_acoustic.get(genre, 30)    
    
    def _estimate_key(self, genre, track_name):
        """Estimate musical key based on genre and track characteristics"""
        # Common keys for different genres
        genre_keys = {
            'pop': ['C', 'G', 'D', 'F'],
            'rock': ['E', 'A', 'D', 'G'],
            'hip-hop': ['C', 'F', 'G', 'A♯/B♭'],
            'electronic': ['C', 'A', 'F♯/G♭', 'D'],
            'indie': ['G', 'C', 'D', 'A'],
            'jazz': ['C', 'F', 'B♭', 'E♭'],
            'folk': ['G', 'C', 'D', 'F'],
            'r&b': ['C', 'F', 'G', 'A♯/B♭']
        }
        
        possible_keys = genre_keys.get(genre, ['C', 'G', 'F', 'D'])
        
        # Use hash of track name to consistently pick a key
        key_index = hash(track_name) % len(possible_keys)
        return possible_keys[key_index]

    def _valence_to_mood(self, valence, energy):
        """Convert valence and energy scores to mood text"""
        if valence >= 70:
            if energy >= 70:
                return "Upbeat, Energetic"
            elif energy >= 50:
                return "Happy, Uplifting"
            else:
                return "Peaceful, Content"
        elif valence >= 50:
            if energy >= 70:
                return "Dynamic, Confident"
            elif energy >= 40:
                return "Balanced, Moderate"
            else:
                return "Calm, Relaxed"
        elif valence >= 30:
            if energy >= 60:
                return "Intense, Dramatic"
            elif energy >= 40:
                return "Melancholic, Thoughtful"
            else:
                return "Mellow, Contemplative"
        else:
            if energy >= 60:
                return "Dark, Aggressive"
            elif energy >= 30:
                return "Sad, Emotional"
            else:
                return "Gloomy, Depressive"
      
    def _get_default_features(self):
        """Return default audio features when API fails"""
        return {
            'tempo': '120 BPM',
            'energy': 65,
            'valence': 55,
            'danceability': 60,
            'acousticness': 30,
            'key': 'C',
            'mode': 'Major',
            'mood': 'Balanced, Moderate'
        }
    
    def _get_key_name(self, key_number):
        """Convert key number to key name"""
        keys = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
        if 0 <= key_number <= 11:
            return keys[key_number]
        return 'Unknown'    
    
    def _estimate_instruments(self, genre):
        """Estimate typical instruments for a genre"""
        instrument_map = {
            'pop': '🎤 Vocals • 🎸 Guitar • 🎹 Piano • 🥁 Drums • 🎛️ Synths',
            'rock': '⚡ Electric Guitar • 🎸 Bass • 🥁 Drums • 🎤 Vocals',
            'hip-hop': '🥁 Drums • 🎸 Bass • 🎛️ Synths • 🎤 Vocals • 📀 Samples',
            'rap': '🥁 Drums • 🎸 Bass • 🎛️ Synths • 🎤 Vocals • 📀 Samples',
            'electronic': '🎛️ Synthesizers • 🥁 Drum Machine • 💻 Computer',
            'dance': '🎛️ Synthesizers • 🥁 Drum Machine • 🎸 Bass',
            'indie': '🎸 Guitar • 🎸 Bass • 🥁 Drums • 🎤 Vocals • 🎹 Piano',
            'folk': '🎸 Acoustic Guitar • 🎤 Vocals • 🎵 Harmonica',
            'country': '🎸 Guitar • 🪕 Banjo • 🎻 Fiddle • 🎤 Vocals • 🥁 Drums',
            'jazz': '🎹 Piano • 🎷 Saxophone • 🎺 Trumpet • 🎸 Bass • 🥁 Drums',
            'blues': '🎸 Guitar • 🎵 Harmonica • 🎹 Piano • 🎸 Bass • 🥁 Drums',
            'reggae': '🎸 Guitar • 🎸 Bass • 🥁 Drums • 🎹 Keyboard',
            'punk': '⚡ Electric Guitar • 🎸 Bass • 🥁 Drums • 🎤 Vocals',
            'metal': '⚡ Electric Guitar • 🎸 Bass • 🥁 Drums • 🎤 Vocals',
            'classical': '🎼 Orchestra • 🎹 Piano • 🎻 Strings • 🎶 Woodwinds',
            'alternative': '🎸 Guitar • 🎸 Bass • 🥁 Drums • 🎤 Vocals • 🎛️ Synths',
            'r&b': '🎤 Vocals • 🎹 Piano • 🎸 Guitar • 🎸 Bass • 🥁 Drums',
            'soul': '🎤 Vocals • 🎹 Piano • 🎸 Guitar • 🎸 Bass • 🥁 Drums',
            'funk': '🎸 Bass • 🎸 Guitar • 🥁 Drums • 🎤 Vocals • 🎺 Horns',
            'ambient': '🎛️ Synthesizers • 🎵 Pads • 🎙️ Field Recordings'
        }
        return instrument_map.get(genre, '🎸 Guitar • 🎹 Piano • 🥁 Drums • 🎤 Vocals')

    def _generate_keywords(self, genre, track_name, artist_name):
        """Generate relevant keywords based on genre and track info"""
        # Base keywords by genre
        genre_keywords = {
            'pop': ['catchy', 'mainstream', 'radio-friendly'],
            'rock': ['powerful', 'energetic', 'guitar-driven'],
            'hip-hop': ['rhythmic', 'urban', 'contemporary'],
            'rap': ['lyrical', 'beats', 'flow'],
            'electronic': ['synthetic', 'digital', 'beats'],
            'dance': ['upbeat', 'club', 'party'],
            'indie': ['alternative', 'creative', 'independent'],
            'folk': ['acoustic', 'traditional', 'storytelling'],
            'country': ['narrative', 'american', 'rural'],
            'jazz': ['improvisation', 'swing', 'smooth'],
            'blues': ['emotional', 'soulful', 'traditional'],
            'reggae': ['rhythmic', 'jamaican', 'laid-back'],
            'punk': ['rebellious', 'fast', 'raw'],
            'metal': ['heavy', 'intense', 'aggressive'],
            'classical': ['orchestral', 'composed', 'timeless'],
            'alternative': ['experimental', 'creative', 'non-mainstream'],
            'r&b': ['smooth', 'soulful', 'groove'],
            'soul': ['emotional', 'passionate', 'heartfelt'],
            'funk': ['groovy', 'rhythmic', 'danceable'],
            'ambient': ['atmospheric', 'relaxing', 'meditative']
        }
        
        keywords = genre_keywords.get(genre, ['music', 'song'])
        
        # Add track-specific keywords
        track_lower = track_name.lower()
        if any(word in track_lower for word in ['love', 'heart', 'baby']):
            keywords.append('romantic')
        if any(word in track_lower for word in ['dance', 'party', 'night']):
            keywords.append('party')
        if any(word in track_lower for word in ['sad', 'cry', 'tear', 'goodbye']):
            keywords.append('emotional')
        if any(word in track_lower for word in ['summer', 'sun', 'beach']):
            keywords.append('summer')
        
        return ', '.join(keywords[:4])  # Limit to 4 keywords

    def _create_music_style(self, artist_name, estimated_genre, popularity):
        """Create an attractive music style description"""
        # Style templates based on popularity and genre
        style_templates = {
            'high_pop': [
                "🔥 Chart-Topping Contemporary {genre} • Radio-Friendly by {artist}",
                "⭐ Billboard-Ready Modern {genre} • Commercial Hit by {artist}",
                "🎯 Mainstream {genre} Sensation • Popular Track by {artist}",
                "💫 Award-Winning {genre} • Chart Success by {artist}"
            ],
            'medium_pop': [
                "🎵 Trending {genre} • Rising Star {artist}",
                "🌟 Contemporary {genre} • Emerging Artist {artist}",
                "🎶 Modern {genre} Sound • Up-and-Coming {artist}",
                "✨ Fresh {genre} • New Wave by {artist}"
            ],
            'low_pop': [
                "💎 Hidden Gem {genre} • Underground by {artist}",
                "🎭 Indie {genre} • Alternative Sound by {artist}",
                "🌙 Intimate {genre} • Artistic Expression by {artist}",
                "🎨 Creative {genre} • Unique Style by {artist}"
            ]
        }
        
        # Determine popularity tier
        if popularity >= 70:
            templates = style_templates['high_pop']
        elif popularity >= 40:
            templates = style_templates['medium_pop']
        else:
            templates = style_templates['low_pop']
        
        # Pick random template and format
        import random
        template = random.choice(templates)
        return template.format(
            genre=estimated_genre.title(),
            artist=artist_name
        )
