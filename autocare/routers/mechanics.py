from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_session
from models import Mechanic, User
from schemas import MechanicPublic
from security import get_current_user
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

router = APIRouter(prefix="/mechanic", tags=["mechanics"])
geolocator = Nominatim(user_agent="autocare")


@router.get("/filter", status_code=HTTPStatus.OK, response_model=List[MechanicPublic])
def get_mechanics_by_filter(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    address: Optional[str] = Query(None),
    rating: Optional[float] = Query(None),
    specialties: Optional[str] = Query(None),
    available_services: Optional[str] = Query(None),
    open24hrs: Optional[bool] = Query(None),
    wifi: Optional[bool] = Query(None),
    take_and_deliver: Optional[bool] = Query(None),
    accessible: Optional[bool] = Query(None),
    waiting_room: Optional[bool] = Query(None),
    limit: int = Query(6, ge=1),  # Limite de elementos por página
    offset: int = Query(0, ge=0),  # Posição inicial dos elementos
):
    # Verificar se o usuário existe
    user = session.scalar(select(User).where(User.id == user.id))

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    # Construir query de filtragem
    mechanics_query = select(Mechanic)

    if rating is not None:
        mechanics_query = mechanics_query.where(
            Mechanic.rating >= rating, Mechanic.rating < rating + 1
        )
    if specialties:
        mechanics_query = mechanics_query.where(Mechanic.specialties.ilike(f"%{specialties}%"))
    if available_services:
        mechanics_query = mechanics_query.where(
            Mechanic.available_services.ilike(f"%{available_services}%")
        )
    if open24hrs is not None:
        mechanics_query = mechanics_query.where(Mechanic.open24hrs == open24hrs)
    if wifi is not None:
        mechanics_query = mechanics_query.where(Mechanic.wifi == wifi)
    if take_and_deliver is not None:
        mechanics_query = mechanics_query.where(Mechanic.take_and_deliver == take_and_deliver)
    if accessible is not None:
        mechanics_query = mechanics_query.where(Mechanic.accessible_ == accessible)
    if waiting_room is not None:
        mechanics_query = mechanics_query.where(Mechanic.waiting_room == waiting_room)

    # Aplicar paginação com limit e offset
    mechanics_query = mechanics_query.limit(limit).offset(offset)

    mechanics = session.execute(mechanics_query).scalars().all()

    if address:
        try:
            user_location = geolocator.geocode(address, timeout=20)

            if not user_location:
                return [MechanicPublic.from_orm(mechanic) for mechanic in mechanics]

            lat1, long1 = user_location.latitude, user_location.longitude

            mechanics_with_distance = []
            for mechanic in mechanics:
                mechanic_location = geolocator.geocode(mechanic.address, timeout=20)

                if mechanic_location:
                    lat2, long2 = mechanic_location.latitude, mechanic_location.longitude
                    distance = geodesic((lat1, long1), (lat2, long2)).kilometers
                    mechanics_with_distance.append((mechanic, distance))
                else:
                    mechanics_with_distance.append((mechanic, float("inf")))

            mechanics_with_distance.sort(key=lambda x: x[1])

            return [MechanicPublic.from_orm(mech) for mech, dist in mechanics_with_distance]

        except (GeocoderTimedOut, GeocoderServiceError):
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="Error with the geolocation service. Please try again later.",
            )

    return [MechanicPublic.from_orm(mechanic) for mechanic in mechanics]
