from rest_framework.views import APIView, Request, Response, status
from .serializers import PetSerializer
from traits.models import Trait
from groups.models import Group
from pets.models import Pet
from rest_framework.pagination import PageNumberPagination


class PetView(APIView, PageNumberPagination):
    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        traits = serializer.validated_data["traits"]
        group = serializer.validated_data["group"]

        serializer.validated_data.pop("traits")

        trait_list = []

        for trait in traits:
            created_trait = Trait.objects.filter(name__iexact=trait["name"]).first()

            if not created_trait:
                created_trait = Trait.objects.create(**trait)

            trait_list.append(created_trait)

        created_group = Group.objects.filter(
            scientific_name__iexact=group["scientific_name"]
        ).first()

        if not created_group:
            created_group = Group.objects.create(**group)

        serializer.validated_data["group"] = created_group

        pet = Pet.objects.create(**serializer.validated_data)

        pet.traits.set(trait_list)

        response = PetSerializer(pet)

        return Response(response.data, status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        trait_param = request.query_params.get("trait", None)

        if trait_param:
            pets = Pet.objects.filter(traits__name=trait_param).all()
        else:
            pets = Pet.objects.all()

        filtered_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(filtered_page, many=True)

        return self.get_paginated_response(serializer.data)

