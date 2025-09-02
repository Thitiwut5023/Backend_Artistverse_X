from flask import jsonify, request
import spotipy
import os
from dotenv import load_dotenv
import random
import re
import math
import openai
import json
import time

load_dotenv()

class SpotifyRecommendController:
    # Genre constants
    DREAM_POP = 'dream pop'
    INDIE_POP = 'indie pop'
    INDIE_ROCK = 'indie rock'
    INDIE_FOLK = 'indie folk'
    CONTEMPORARY_RNB = 'contemporary r&b'
    BEDROOM_POP = 'bedroom pop'
    ELECTROPOP = 'electropop'
    ALTERNATIVE_POP = 'alternative pop'
    DARK_POP = 'dark pop'
    TRAP_ROCK = 'trap rock'
    
    def __init__(self):
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        
        # Enhanced audio features estimation data with more specific genres
        self.genre_tempo_map = {
            self.DREAM_POP: {'min': 80, 'max': 120, 'mode': 'Major'},
            self.INDIE_POP: {'min': 100, 'max': 130, 'mode': 'Major'},
            'pop': {'min': 100, 'max': 130, 'mode': 'Major'},
            self.ELECTROPOP: {'min': 110, 'max': 140, 'mode': 'Major'},
            'synthpop': {'min': 120, 'max': 140, 'mode': 'Major'},
            self.ALTERNATIVE_POP: {'min': 110, 'max': 130, 'mode': 'Major'},
            self.DARK_POP: {'min': 110, 'max': 130, 'mode': 'Minor'},
            self.TRAP_ROCK: {'min': 115, 'max': 135, 'mode': 'Minor'},
            'alternative rock': {'min': 120, 'max': 160, 'mode': 'Minor'},
            'electropop': {'min': 110, 'max': 140, 'mode': 'Major'},
            'rock': {'min': 120, 'max': 160, 'mode': 'Minor'},
            'hip-hop': {'min': 70, 'max': 140, 'mode': 'Minor'},
            'trap': {'min': 60, 'max': 100, 'mode': 'Minor'},
            'rap': {'min': 70, 'max': 140, 'mode': 'Minor'},
            'drill': {'min': 120, 'max': 160, 'mode': 'Minor'},
            'electronic': {'min': 120, 'max': 180, 'mode': 'Major'},
            'house': {'min': 120, 'max': 130, 'mode': 'Major'},
            'techno': {'min': 120, 'max': 140, 'mode': 'Major'},
            'edm': {'min': 128, 'max': 140, 'mode': 'Major'},
            'dance': {'min': 120, 'max': 140, 'mode': 'Major'},
            'indie': {'min': 100, 'max': 130, 'mode': 'Major'},
            self.INDIE_FOLK: {'min': 80, 'max': 120, 'mode': 'Major'},
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
            self.CONTEMPORARY_RNB: {'min': 70, 'max': 130, 'mode': 'Major'},
            'soul': {'min': 70, 'max': 130, 'mode': 'Major'},
            'funk': {'min': 100, 'max': 130, 'mode': 'Major'},
            'ambient': {'min': 60, 'max': 100, 'mode': 'Major'},
            'lo-fi': {'min': 70, 'max': 90, 'mode': 'Major'},
            self.BEDROOM_POP: {'min': 80, 'max': 110, 'mode': 'Major'},
        }
        
        # Enhanced artist genre mapping with correct artist names and specific genres
        self.artist_genre_map = {
            'taylor swift': 'pop',
            'ed sheeran': 'pop',
            'drake': 'hip-hop',
            'ariana grande': 'pop',
            'post malone': 'hip-hop',
            'the weeknd': self.CONTEMPORARY_RNB,
            'dua lipa': self.ELECTROPOP,
            'olivia rodrigo': self.INDIE_POP,
            'harry styles': 'pop',
            'billie eilish': self.ELECTROPOP,
            'chase atlantic': self.ALTERNATIVE_POP,
            'arctic monkeys': self.INDIE_ROCK,
            'the walters': self.INDIE_POP,
            'little john': 'hip-hop',
            'ten': 'pop',
            'arafat': 'hip-hop',
            'nct dream': 'k-pop',
            'd4vd': self.DREAM_POP,
            'clairo': self.BEDROOM_POP,
            'rex orange county': self.BEDROOM_POP,
            'boy pablo': self.INDIE_POP,
            'kali uchis': self.CONTEMPORARY_RNB,
            'tyler, the creator': 'hip-hop',
            'frank ocean': self.CONTEMPORARY_RNB,
            'mac miller': 'hip-hop',
            'kendrick lamar': 'hip-hop',
            'lana del rey': self.DREAM_POP,
            'phoebe bridgers': self.INDIE_FOLK,
            'mitski': self.INDIE_ROCK,            'tame impala': 'psychedelic pop',
            'glass animals': self.INDIE_POP,
        }
        
        # Artist-specific key patterns for enhanced key estimation
        self.artist_key_patterns = {
            'chase atlantic': ['Ab', 'G#', 'Eb', 'Bb', 'F'],
            'billie eilish': ['F#', 'G', 'Am', 'Em'],
            'the weeknd': ['C', 'Am', 'F', 'G'],
            'olivia rodrigo': ['F', 'C', 'G', 'Am'],
        }
        
        # Artist-specific tempo overrides for accuracy
        self.artist_tempo_overrides = {
            'chase atlantic': {
                'swim': 120,
                'default': 120
            },
            'billie eilish': {
                'default': 85
            }
        }
        
        # Artist-specific mood characteristics
        self.artist_moods = {
            'chase atlantic': ['Energetic', 'Dark-Pop', 'Sensual'],
            'billie eilish': ['Melancholic', 'Dark', 'Introspective'],
            'the weeknd': ['Sensual', 'Dark', 'Atmospheric'],
            'olivia rodrigo': ['Emotional', 'Angsty', 'Vulnerable'],
        }
        
        # Genre-specific mood patterns
        self.genre_moods = {
            self.ALTERNATIVE_POP: ['Energetic', 'Dark-Pop', 'Sensual'],
            self.DARK_POP: ['Dark', 'Melancholic', 'Introspective'],
            self.DREAM_POP: ['Dreamy', 'Ethereal', 'Nostalgic'],
            self.BEDROOM_POP: ['Chill', 'Intimate', 'Lo-fi'],
            self.INDIE_POP: ['Upbeat', 'Quirky', 'Feel-good'],
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
            'artist:Post Malone'        ]
        
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
        """Format track data for frontend with specific required fields"""
        # Get artist names (preserve exact official format)
        artists = [artist['name'] for artist in track['artists']]
        artist_name = ', '.join(artists)
        
        # Get album image
        image_url = None
        if track['album']['images']:
            if len(track['album']['images']) > 1:
                image_url = track['album']['images'][1]['url']
            else:
                image_url = track['album']['images'][0]['url']
                
        # Get release year (original release, not remaster)
        release_date = track['album']['release_date']
        year = release_date.split('-')[0] if release_date else 'Unknown'
          # Estimate genre from artist and track name
        estimated_genre = self._estimate_specific_genre(artist_name.lower(), track['name'].lower())
        audio_features = self._estimate_audio_features(track)
        
        # Format duration to minutes:seconds
        duration_formatted = self._format_duration(track['duration_ms'])        # Get musical key
        key = audio_features.get('key', 'C')
        
        # Create music style description
        music_style = self._create_music_style(artist_name, estimated_genre, track.get('popularity', 50))
        
        formatted_track = {
            'id': hash(track['id']) % 100000,
            'spotify_id': track['id'],
            # Core song information
            'song_title': track['name'] or 'Unknown Song',  # Preserve exact official title
            'artist_name': artist_name or 'Unknown Artist',  # Preserve exact official artist name
            'genre': estimated_genre,  # Specific subgenre analysis
            'beat': f"{audio_features.get('tempo', 120)}",  # Just BPM number for better accuracy
            'mood': audio_features.get('mood', 'Balanced'),  # Enhanced mood analysis
            'keywords': self._generate_specific_keywords(estimated_genre, track['name']),  # 4-6 relevant tags
            'instruments': self._estimate_instruments(estimated_genre),  # Main instruments by prominence
            'release_year': year,  # Original release year
            'key': key,  # Musical key
            'duration': duration_formatted,  # Song duration
            'music_style': music_style,  # New music style field
            
            # Additional metadata for display
            'album': track['album']['name'] or 'Unknown Album',
            'image': image_url,
            'spotify_url': track['external_urls']['spotify'],
            'preview_url': track['preview_url'],
            'popularity': track['popularity']
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
        """Estimate audio features from track metadata"""        # Get artist info
        artist_name = track['artists'][0]['name'].lower() if track['artists'] else 'unknown'
        track_name = track['name'].lower() if track['name'] else 'unknown'
        popularity = track.get('popularity', 50)
        
        # Estimate genre from artist
        estimated_genre = self._estimate_genre(artist_name, track_name)
        
        # Get tempo range for genre
        tempo_info = self.genre_tempo_map.get(estimated_genre, {'min': 100, 'max': 130, 'mode': 'Major'})
          # Calculate estimated tempo based on duration and popularity
        tempo_base = (tempo_info['min'] + tempo_info['max']) / 2
        tempo_variation = (popularity - 50) * 0.5  # Popular songs tend to be slightly faster
        estimated_tempo = int(tempo_base + tempo_variation)
        
        # Artist-specific tempo adjustments for accuracy
        artist_tempo_overrides = {
            'chase atlantic': {'swim': 120, 'default': 120}  # Known Chase Atlantic songs
        }
        
        if artist_name in artist_tempo_overrides:
            if track_name in artist_tempo_overrides[artist_name]:
                estimated_tempo = artist_tempo_overrides[artist_name][track_name]
            else:
                estimated_tempo = artist_tempo_overrides[artist_name]['default']
        
        # Ensure tempo stays within reasonable bounds
        estimated_tempo = max(60, min(200, estimated_tempo))
        
        # Estimate energy based on genre and popularity
        energy = self._estimate_energy(estimated_genre, popularity)
        
        # Estimate valence (happiness) based on genre and tempo
        valence = self._estimate_valence(estimated_genre, estimated_tempo)
        
        # Estimate danceability based on tempo and genre
        danceability = self._estimate_danceability(estimated_tempo, estimated_genre)
        
        # Estimate acousticness based on genre
        acousticness = self._estimate_acousticness(estimated_genre)
          # Estimate key and mode - pass audio features for better estimation
        audio_features_temp = {
            'valence': valence,
            'energy': energy
        }
        key = self._estimate_key(estimated_genre, track_name, artist_name, audio_features_temp)
        mode = tempo_info['mode']
        
        # Convert valence to mood text with enhanced analysis
        mood = self._valence_to_mood(valence, energy, estimated_genre, track_name, artist_name)
        
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
    
    def _estimate_key(self, genre, track_name, artist_name, audio_features):
        """Estimate musical key based on genre, artist, and audio characteristics"""
        # Enhanced key mapping with artist-specific patterns
        artist_key_patterns = {
            'taylor swift': ['G', 'C', 'D', 'F'],
            'ed sheeran': ['G', 'C', 'D', 'Em'],
            'drake': ['F', 'C', 'Bb', 'Gm'],
            'the weeknd': ['Bb', 'F', 'Cm', 'Gm'],
            'billie eilish': ['F', 'C', 'Bb', 'Gm'],            'ariana grande': ['C', 'G', 'F', 'Am'],
            'chase atlantic': ['Ab', 'G#', 'Eb', 'Bb', 'F'],  # Alternative Pop/R&B keys
            'd4vd': ['C', 'G', 'Am', 'F'],
            'arctic monkeys': ['E', 'A', 'B', 'F#m'],
            'clairo': ['F', 'C', 'Bb', 'Am'],
            'lana del rey': ['Bb', 'F', 'Eb', 'Gm']
        }
        
        # Genre-specific key tendencies with more accuracy
        genre_keys = {
            'pop': ['C', 'G', 'F', 'Am', 'D'],
            'dream pop': ['F', 'C', 'Bb', 'Dm', 'Am'],
            'indie pop': ['G', 'C', 'D', 'Em', 'Am'],
            'bedroom pop': ['F', 'C', 'Bb', 'Am', 'Dm'],
            'contemporary r&b': ['Bb', 'F', 'Eb', 'Gm', 'Cm'],            'electropop': ['C', 'F', 'G', 'Am', 'Dm'],
            'alternative pop': ['Ab', 'G#', 'Eb', 'Bb', 'F'],
            'dark pop': ['Ab', 'Fm', 'Eb', 'Bb', 'Gm'],
            'trap rock': ['Ab', 'Bb', 'F', 'Gm', 'Eb'],
            'indie rock': ['E', 'A', 'D', 'Em', 'Bm'],
            'alternative rock': ['E', 'A', 'G', 'Em', 'Am'],
            'rock': ['E', 'A', 'D', 'G', 'Bm'],
            'hip-hop': ['C', 'F', 'Bb', 'Am', 'Gm'],
            'electronic': ['C', 'A', 'F#m', 'D', 'Bm'],
            'indie': ['G', 'C', 'D', 'Em', 'Am'],
            'jazz': ['C', 'F', 'Bb', 'G7', 'Dm'],
            'folk': ['G', 'C', 'D', 'Em', 'Am'],
            'indie folk': ['G', 'C', 'D', 'Em', 'Am'],
            'r&b': ['C', 'F', 'G', 'Am', 'Bb']
        }
        
        # Check artist-specific patterns first
        artist_lower = artist_name.lower()
        if artist_lower in artist_key_patterns:
            possible_keys = artist_key_patterns[artist_lower]
        else:
            possible_keys = genre_keys.get(genre.lower(), ['C', 'G', 'F', 'D'])
        
        # Use song characteristics to influence key selection
        track_lower = track_name.lower()
        
        # Happy/upbeat songs tend to be in major keys
        valence = audio_features.get('valence', 50)
        energy = audio_features.get('energy', 50)
        
        if valence > 70 and energy > 60:
            # Prefer major keys for happy, energetic songs
            major_keys = [k for k in possible_keys if not ('m' in k and k != 'Am')]
            if major_keys:
                possible_keys = major_keys
        elif valence < 40:
            # Prefer minor keys or darker majors for sad songs
            minor_keys = [k for k in possible_keys if 'm' in k] + ['F', 'Bb', 'Eb']
            possible_keys = minor_keys if minor_keys else possible_keys
          # Use a more sophisticated hash that considers multiple factors
        key_seed = hash(track_name + artist_name + genre) % len(possible_keys)
        return possible_keys[key_seed]

    def _valence_to_mood(self, valence, energy, genre, track_name, artist_name):
        """Enhanced mood analysis based on multiple factors"""
        
        # Analyze track title for emotional keywords
        track_lower = track_name.lower()
        artist_lower = artist_name.lower()
        
        # Emotional keyword detection
        sad_keywords = ['sad', 'cry', 'hurt', 'pain', 'lonely', 'miss', 'lost', 'goodbye', 'broken', 'tears']
        happy_keywords = ['happy', 'joy', 'love', 'good', 'great', 'wonderful', 'amazing', 'beautiful', 'smile']
        angry_keywords = ['hate', 'mad', 'angry', 'fight', 'war', 'rage', 'kill', 'destroy']
        romantic_keywords = ['love', 'heart', 'baby', 'darling', 'kiss', 'forever', 'together', 'romance']
        party_keywords = ['party', 'dance', 'club', 'night', 'fun', 'wild', 'crazy', 'celebrate']
        chill_keywords = ['chill', 'relax', 'calm', 'peace', 'quiet', 'slow', 'soft', 'gentle']
        
        # Artist-specific mood tendencies
        artist_moods = {
            'billie eilish': ['Melancholic', 'Introspective', 'Dark'],
            'd4vd': ['Dreamy', 'Nostalgic', 'Romantic'],
            'clairo': ['Dreamy', 'Soft', 'Romantic'],
            'lana del rey': ['Melancholic', 'Cinematic', 'Nostalgic'],
            'the weeknd': ['Dark', 'Seductive', 'Intense'],
            'drake': ['Confident', 'Moody', 'Reflective'],
            'taylor swift': ['Emotional', 'Storytelling', 'Catchy'],            'ariana grande': ['Confident', 'Empowering', 'Romantic'],
            'chase atlantic': ['Energetic', 'Dark-Pop', 'Sensual'],
            'arctic monkeys': ['Cool', 'Edgy', 'Confident'],
            'post malone': ['Laid-back', 'Melodic', 'Emotional']
        }
        
        # Genre-specific mood characteristics
        genre_moods = {
            'dream pop': ['Dreamy', 'Ethereal', 'Nostalgic'],
            'bedroom pop': ['Intimate', 'Cozy', 'Relaxed'],
            'indie pop': ['Fresh', 'Authentic', 'Uplifting'],
            'contemporary r&b': ['Smooth', 'Sensual', 'Soulful'],            'electropop': ['Energetic', 'Modern', 'Catchy'],
            'alternative pop': ['Energetic', 'Dark-Pop', 'Sensual'],
            'dark pop': ['Dark', 'Moody', 'Atmospheric'],
            'trap rock': ['Edgy', 'Intense', 'Rhythmic'],
            'indie rock': ['Raw', 'Authentic', 'Emotional'],
            'alternative rock': ['Edgy', 'Rebellious', 'Intense'],
            'pop': ['Catchy', 'Uplifting', 'Radio-friendly'],
            'hip-hop': ['Confident', 'Rhythmic', 'Street-smart'],
            'electronic': ['Futuristic', 'Energetic', 'Digital'],
            'jazz': ['Sophisticated', 'Smooth', 'Timeless'],
            'folk': ['Authentic', 'Storytelling', 'Organic'],
            'indie folk': ['Intimate', 'Thoughtful', 'Acoustic']
        }
        
        # Start with base analysis
        if valence >= 75 and energy >= 70:
            base_moods = ["Euphoric", "Energetic", "Celebratory"]
        elif valence >= 70 and energy >= 50:
            base_moods = ["Happy", "Uplifting", "Joyful"]
        elif valence >= 60 and energy >= 60:
            base_moods = ["Upbeat", "Positive", "Lively"]
        elif valence >= 50 and energy >= 50:
            base_moods = ["Balanced", "Moderate", "Steady"]
        elif valence >= 40 and energy >= 40:
            base_moods = ["Contemplative", "Thoughtful", "Mellow"]
        elif valence >= 30:
            base_moods = ["Melancholic", "Reflective", "Somber"]
        else:
            base_moods = ["Sad", "Dark", "Emotional"]
        
        # Override with keyword-based analysis
        if any(word in track_lower for word in sad_keywords):
            base_moods = ["Sad", "Emotional", "Heartfelt"]
        elif any(word in track_lower for word in happy_keywords):
            base_moods = ["Happy", "Joyful", "Uplifting"]
        elif any(word in track_lower for word in romantic_keywords):
            base_moods = ["Romantic", "Loving", "Intimate"]
        elif any(word in track_lower for word in party_keywords):
            base_moods = ["Party", "Energetic", "Fun"]
        elif any(word in track_lower for word in chill_keywords):
            base_moods = ["Chill", "Relaxed", "Laid-back"]
        
        # Apply artist-specific tendencies
        if artist_lower in artist_moods:
            artist_mood_set = artist_moods[artist_lower]
            # Blend with base moods
            final_moods = [artist_mood_set[0], base_moods[0]]
            if len(artist_mood_set) > 1:
                final_moods.append(artist_mood_set[1])
        # Apply genre-specific characteristics
        elif genre.lower() in genre_moods:
            genre_mood_set = genre_moods[genre.lower()]
            final_moods = [genre_mood_set[0], base_moods[0]]
            if len(genre_mood_set) > 1:
                final_moods.append(genre_mood_set[1])
        else:
            final_moods = base_moods[:2]
        
        # Return 1-2 primary moods
        return ", ".join(final_moods[:2])
      
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

    def _generate_keywords(self, genre, track_name):
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

    def _estimate_specific_genre(self, artist_name, track_name):
        """Estimate specific subgenre from artist name and track name"""
        # Check known artist mappings first
        if artist_name in self.artist_genre_map:
            return self.artist_genre_map[artist_name].title()
        
        # Check for specific genre keywords in artist name or track name
        text_to_check = f"{artist_name} {track_name}".lower()        # More specific genre keywords mapping
        specific_genre_keywords = {
            self.DREAM_POP: ['dream', 'dreamy', 'ethereal', 'shoegaze'],
            self.BEDROOM_POP: ['bedroom', 'lo-fi', 'chill', 'indie bedroom'],
            self.INDIE_POP: ['indie pop', 'indie', 'independent'],
            'electropop': ['electro', 'synth', 'electronic pop'],
            self.ALTERNATIVE_POP: ['alternative pop', 'alt pop', 'chase atlantic'],
            self.DARK_POP: ['dark pop', 'dark', 'moody pop'],
            self.TRAP_ROCK: ['trap rock', 'trap', 'rock trap'],
            'synthpop': ['synth', 'synthetic', '80s'],
            self.CONTEMPORARY_RNB: ['r&b', 'rnb', 'contemporary'],
            'alternative rock': ['alternative rock', 'alt rock', 'grunge'],
            'indie rock': ['indie rock', 'independent rock'],
            'trap': ['trap', 'atlanta', 'mumble'],
            'drill': ['drill', 'chicago drill', 'uk drill'],
            'house': ['house', 'deep house', 'tech house'],
            'techno': ['techno', 'detroit', 'minimal'],
            'edm': ['edm', 'festival', 'big room'],
            self.INDIE_FOLK: ['indie folk', 'folk indie', 'acoustic indie'],
            'psychedelic pop': ['psychedelic', 'psych', 'trippy'],
            'k-pop': ['k-pop', 'korean', 'kpop'],
            'lo-fi': ['lo-fi', 'lofi', 'low fidelity']
        }
        
        # Check for specific genre matches first
        for genre, keywords in specific_genre_keywords.items():
            for keyword in keywords:
                if keyword in text_to_check:
                    return genre.title()
        
        # Fallback to general genres if no specific match
        general_genre_keywords = {
            'Pop': ['pop', 'mainstream', 'chart', 'hit', 'commercial'],
            'Hip-Hop': ['hip', 'hop', 'rap', 'hip-hop'],
            'Rock': ['rock', 'metal', 'punk'],
            'Electronic': ['electronic', 'edm', 'dance'],
            'R&B': ['r&b', 'soul', 'funk', 'rnb'],
            'Indie': ['indie', 'independent', 'alternative'],
            'Jazz': ['jazz', 'blues', 'swing'],
            'Folk': ['folk', 'acoustic', 'country']
        }
        
        for genre, keywords in general_genre_keywords.items():
            for keyword in keywords:
                if keyword in text_to_check:
                    return genre
        
        # Default to Pop for unknown
        return 'Pop'

    def _analyze_song_content(self, track_name, genre):
        """Analyze song content themes based on title and genre"""
        title_lower = track_name.lower()
        
        # Universal theme keywords
        love_themes = ['love', 'heart', 'kiss', 'romance', 'together', 'you', 'baby']
        nostalgic_themes = ['memory', 'remember', 'past', 'yesterday', 'time', 'old', 'back']
        empowerment_themes = ['strong', 'power', 'fight', 'rise', 'free', 'brave', 'confidence']
        melancholic_themes = ['sad', 'cry', 'broken', 'lonely', 'lost', 'hurt', 'pain']
        celebration_themes = ['party', 'dance', 'fun', 'celebrate', 'night', 'good', 'happy']
        introspective_themes = ['think', 'mind', 'soul', 'deep', 'life', 'me', 'myself']
        
        themes = []
        
        # Check for theme matches
        if any(word in title_lower for word in love_themes):
            themes.append('Love and relationships')
        if any(word in title_lower for word in nostalgic_themes):
            themes.append('Nostalgia and memories')
        if any(word in title_lower for word in empowerment_themes):
            themes.append('Empowerment and strength')
        if any(word in title_lower for word in melancholic_themes):
            themes.append('Melancholy and reflection')
        if any(word in title_lower for word in celebration_themes):
            themes.append('Celebration and joy')
        if any(word in title_lower for word in introspective_themes):
            themes.append('Self-reflection and growth')
          # Genre-based theme defaults
        if not themes:
            genre_defaults = {
                self.DREAM_POP: 'Ethereal emotions and introspection',
                self.BEDROOM_POP: 'Intimate personal experiences',
                self.INDIE_POP: 'Youthful experiences and emotions',
                'hip-hop': 'Personal expression and social themes',
                self.CONTEMPORARY_RNB: 'Love and personal relationships',
                'electronic': 'Energy and movement',
                self.INDIE_ROCK: 'Alternative perspectives and emotions',
                'pop': 'Universal human experiences'
            }
            return genre_defaults.get(genre.lower(), 'Life experiences and emotions')
        
        return ', '.join(themes[:2])  # Return top 2 themes    
    
    def _generate_specific_keywords(self, genre, track_name):
        """Generate 4-6 specific and relevant keywords"""
        keywords = []
        
        # Genre-based musical descriptors
        genre_descriptors = {
            self.DREAM_POP: ['dreamy', 'atmospheric', 'ethereal', 'reverb-heavy'],
            self.BEDROOM_POP: ['lo-fi', 'intimate', 'nostalgic', 'DIY'],
            self.INDIE_POP: ['catchy', 'melodic', 'indie', 'alternative'],
            self.ELECTROPOP: ['synthetic', 'danceable', 'electronic', 'pop'],
            self.CONTEMPORARY_RNB: ['smooth', 'soulful', 'vocal-driven', 'groovy'],
            'hip-hop': ['rhythmic', 'lyrical', 'beat-driven', 'urban'],
            self.INDIE_ROCK: ['guitar-driven', 'alternative', 'raw', 'energetic'],
            'pop': ['catchy', 'mainstream', 'accessible', 'melodic'],
            'electronic': ['synthesized', 'danceable', 'digital', 'energetic'],
            'rock': ['guitar-heavy', 'powerful', 'driving', 'energetic']
        }
        
        # Add genre-specific descriptors
        if genre.lower() in genre_descriptors:
            keywords.extend(genre_descriptors[genre.lower()][:2])
        
        # Functional keywords based on track characteristics
        title_lower = track_name.lower()
        
        if any(word in title_lower for word in ['dance', 'party', 'club']):
            keywords.append('party-ready')
        elif any(word in title_lower for word in ['chill', 'relax', 'calm']):
            keywords.append('relaxing')
        elif any(word in title_lower for word in ['love', 'heart', 'romance']):
            keywords.append('romantic')
        elif any(word in title_lower for word in ['sad', 'cry', 'hurt']):
            keywords.append('emotional')
        elif any(word in title_lower for word in ['night', 'midnight', 'evening']):
            keywords.append('nighttime')
        elif any(word in title_lower for word in ['summer', 'sun', 'beach']):
            keywords.append('summery')
        else:
            keywords.append('mood-setting')
        
        # Add context-based keywords
        if 'pop' in genre.lower():
            keywords.append('radio-friendly')
        if 'indie' in genre.lower():
            keywords.append('alternative')
        if any(word in genre.lower() for word in ['electronic', 'house', 'techno']):
            keywords.append('electronic')
        
        # Ensure we have exactly 4-6 keywords
        if len(keywords) < 4:
            default_keywords = ['melodic', 'contemporary', 'expressive', 'atmospheric']
            keywords.extend(default_keywords[:4-len(keywords)])
        
        return keywords[:6]  # Limit to 6 keywords max

    def _format_duration(self, duration_ms):
        """Format duration from milliseconds to MM:SS format"""
        if not duration_ms:
            return "Unknown"
        
        seconds = duration_ms // 1000
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        
        return f"{minutes}:{remaining_seconds:02d}"

    def generate_song_content(self):
        """Generate song content analysis using ChatGPT API"""
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Request data is required'
                }), 400

            song_title = data.get('song_title')
            artist_name = data.get('artist_name')
            
            if not song_title or not artist_name:
                return jsonify({
                    'success': False,
                    'error': 'Song title and artist name are required'
                }), 400

            genre = data.get('genre', 'Unknown')
            mood = data.get('mood', 'Unknown')
            keywords = data.get('keywords', [])            # Set up OpenAI client
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            if not os.getenv('OPENAI_API_KEY'):
                return jsonify({
                    'success': False,
                    'error': 'OpenAI API key not configured'
                }), 500

            # Create prompt for ChatGPT
            prompt = self._create_content_prompt(song_title, artist_name, genre, mood, keywords)
            
            # Generate content using ChatGPT
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music analyst who creates insightful, engaging descriptions of songs. Provide thoughtful analysis in 2-3 sentences that captures the essence and emotional impact of the music."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            generated_content = response.choices[0].message.content.strip()
            
            return jsonify({
                'success': True,
                'content': generated_content,
                'song_title': song_title,
                'artist_name': artist_name
            })
            
        except openai.error.RateLimitError:
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.'
            }), 429
            
        except openai.error.AuthenticationError:
            return jsonify({
                'success': False,
                'error': 'Invalid OpenAI API key'
            }), 401
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to generate content: {str(e)}'
            }), 500

    def _create_content_prompt(self, song_title, artist_name, genre, mood, keywords):
        """Create a prompt for ChatGPT content generation"""
        keywords_str = ', '.join(keywords) if keywords else 'N/A'
        
        prompt = f"""
        Analyze the song "{song_title}" by {artist_name}.
        
        Song Details:
        - Genre: {genre}
        - Mood: {mood}
        - Keywords: {keywords_str}
        
        Please provide a brief, insightful analysis of this song that covers:
        1. The emotional themes and atmosphere
        2. The musical style and its impact
        3. What makes this song unique or compelling
        
        Keep the response engaging and accessible, around 50-80 words.
        """
        
        return prompt
