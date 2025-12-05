from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class User:
	user_id: int
	username: str
	session_id: str
	is_host: bool = False

@dataclass
class VideoState:
	source: str = ""
	current_time: float = 0.0
	is_playing: bool = False
	anime_id: Optional[int] = None
	anime_title: Optional[str] = None
	episode: int = 0
	season_url: Optional[str] = None
	last_update: datetime = field(default_factory=datetime.now)

@dataclass
class Room:
	room_id: str
	name: str
	host_user_id: int
	created_by_user_id: int
	users: Dict[str, User] = field(default_factory=dict)  # session_id -> User
	video_state: VideoState = field(default_factory=VideoState)
	created_at: datetime = field(default_factory=datetime.now)

class RoomManager:
	def __init__(self):
		self.rooms: Dict[str, Room] = {}  # room_id -> Room
		self.user_sessions: Dict[int, List[str]] = {}  # user_id -> [session_ids]
		self.session_to_room: Dict[str, str] = {}  # session_id -> room_id

	def create_room(self, user_id: int, username: str, room_name: Optional[str] = None) -> Optional[Room]:
		"""Create a new room. Returns None if user already has 2 rooms."""
		# Check if user already created 2 rooms
		user_created_rooms = [room for room in self.rooms.values() if room.created_by_user_id == user_id]
		if len(user_created_rooms) >= 2:
			return None

		room_id = str(uuid.uuid4())
		if not room_name:
			room_name = f"Salon de {username}"

		room = Room(
			room_id=room_id,
			name=room_name,
			host_user_id=user_id,
			created_by_user_id=user_id
		)
		self.rooms[room_id] = room
		return room

	def join_room(self, room_id: str, user_id: int, username: str, session_id: str) -> Optional[Dict]:
		"""
		Join a room. Returns error dict if:
		- Room doesn't exist
		- User already in room with same user_id (unless reconnecting)
		Returns room state if successful.
		"""
		room = self.rooms.get(room_id)
		if not room:
			return {"error": "Room not found"}

		# Check if this user_id is already in the room with a different session
		old_session_id = None
		was_host = False
		for sess_id, user in room.users.items():
			if user.user_id == user_id and sess_id != session_id:
				# User is reconnecting with a new session
				old_session_id = sess_id
				was_host = user.is_host
				break

		# If user is reconnecting, remove old session
		if old_session_id:
			print(f"[RoomManager] User {user_id} reconnecting, removing old session {old_session_id}")
			room.users.pop(old_session_id, None)
			if user_id in self.user_sessions:
				if old_session_id in self.user_sessions[user_id]:
					self.user_sessions[user_id].remove(old_session_id)
			if old_session_id in self.session_to_room:
				del self.session_to_room[old_session_id]

		# Determine if user should be host
		if was_host:
			# User was host before, keep them as host
			is_host = True
		elif user_id == room.host_user_id and len(room.users) == 0:
			# First user joining and they're the designated host
			is_host = True
		else:
			is_host = False

		# Add user to room
		user = User(
			user_id=user_id,
			username=username,
			session_id=session_id,
			is_host=is_host
		)
		room.users[session_id] = user

		# Track session
		if user_id not in self.user_sessions:
			self.user_sessions[user_id] = []
		self.user_sessions[user_id].append(session_id)
		self.session_to_room[session_id] = room_id

		return self.get_room_state(room_id)

	def leave_room(self, session_id: str) -> Optional[str]:
		"""Remove user from room. Returns room_id if room should be deleted (empty)."""
		room_id = self.session_to_room.get(session_id)
		if not room_id:
			return None

		room = self.rooms.get(room_id)
		if not room:
			return None

		user = room.users.pop(session_id, None)
		if user:
			# Clean up session tracking
			if user.user_id in self.user_sessions:
				self.user_sessions[user.user_id].remove(session_id)
				if not self.user_sessions[user.user_id]:
					del self.user_sessions[user.user_id]
			del self.session_to_room[session_id]

			# If user was host and room not empty, transfer host
			if user.is_host and room.users:
				new_host_session = next(iter(room.users.keys()))
				room.users[new_host_session].is_host = True
				room.host_user_id = room.users[new_host_session].user_id

		# Delete room if empty
		if not room.users:
			del self.rooms[room_id]
			return room_id

		return None

	def transfer_host(self, room_id: str, new_host_user_id: int, requester_session_id: str) -> Optional[Dict]:
		"""Transfer host to another user. Returns error dict or success."""
		room = self.rooms.get(room_id)
		if not room:
			return {"error": "Room not found"}

		requester = room.users.get(requester_session_id)
		if not requester or not requester.is_host:
			return {"error": "Only host can transfer"}

		# Find new host by user_id
		new_host = None
		for user in room.users.values():
			if user.user_id == new_host_user_id:
				new_host = user
				break

		if not new_host:
			return {"error": "New host not in room"}

		# Transfer
		requester.is_host = False
		new_host.is_host = True
		room.host_user_id = new_host_user_id

		return {"success": True, "new_host_id": new_host_user_id}

	def update_video_state(self, room_id: str, session_id: str, **kwargs) -> Optional[Dict]:
		"""Update video state. Only host can update. Returns error or new state."""
		room = self.rooms.get(room_id)
		if not room:
			return {"error": "Room not found"}

		user = room.users.get(session_id)
		if not user or not user.is_host:
			return {"error": "Only host can control video"}

		# Update video state
		if "source" in kwargs:
			room.video_state.source = kwargs["source"]
		if "current_time" in kwargs:
			room.video_state.current_time = kwargs["current_time"]
		if "is_playing" in kwargs:
			room.video_state.is_playing = kwargs["is_playing"]
		if "anime_id" in kwargs:
			room.video_state.anime_id = kwargs["anime_id"]
		if "anime_title" in kwargs:
			room.video_state.anime_title = kwargs["anime_title"]
		if "episode" in kwargs:
			room.video_state.episode = kwargs["episode"]
		if "season_url" in kwargs:
			room.video_state.season_url = kwargs["season_url"]

		room.video_state.last_update = datetime.now()

		return self.get_video_state(room_id)

	def get_room_state(self, room_id: str) -> Optional[Dict]:
		"""Get full room state."""
		room = self.rooms.get(room_id)
		if not room:
			return None

		return {
			"room_id": room.room_id,
			"name": room.name,
			"host_user_id": room.host_user_id,
			"users": [
				{
					"user_id": user.user_id,
					"username": user.username,
					"is_host": user.is_host
				}
				for user in room.users.values()
			],
			"video_state": {
				"source": room.video_state.source,
				"current_time": room.video_state.current_time,
				"is_playing": room.video_state.is_playing,
				"anime_id": room.video_state.anime_id,
				"anime_title": room.video_state.anime_title,
				"episode": room.video_state.episode,
				"season_url": room.video_state.season_url
			}
		}

	def get_video_state(self, room_id: str) -> Optional[Dict]:
		"""Get just video state."""
		room = self.rooms.get(room_id)
		if not room:
			return None

		return {
			"source": room.video_state.source,
			"current_time": room.video_state.current_time,
			"is_playing": room.video_state.is_playing,
			"anime_id": room.video_state.anime_id,
			"anime_title": room.video_state.anime_title,
			"episode": room.video_state.episode,
			"season_url": room.video_state.season_url
		}

	def get_all_rooms(self) -> List[Dict]:
		"""Get list of all rooms."""
		return [
			{
				"room_id": room.room_id,
				"name": room.name,
				"user_count": len(room.users),
				"host_user_id": room.host_user_id,
				"created_by_user_id": room.created_by_user_id
			}
			for room in self.rooms.values()
		]

	def get_room_by_session(self, session_id: str) -> Optional[str]:
		"""Get room_id from session_id."""
		return self.session_to_room.get(session_id)
