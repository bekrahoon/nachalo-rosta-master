import { MapPin, Calendar, ExternalLink, Globe, Building2, Sparkles, Bookmark } from 'lucide-react';

const formatDate = (value) => {
  if (!value) return null;
  try {
    return new Date(value).toLocaleDateString('ru-RU');
  } catch {
    return null;
  }
};

export const ListingCard = ({ listing, matchScore, reason, isSaved, onToggleSave }) => {
  const startDate = formatDate(listing.start_date);
  const deadline = formatDate(listing.application_deadline);

  return (
    <div className="card bg-base-100 shadow-lg hover:shadow-xl transition relative">
      {onToggleSave && (
        <button
          type="button"
          className={`btn btn-circle btn-sm absolute top-2 left-2 z-10 ${isSaved ? 'btn-primary' : 'btn-ghost bg-base-100'}`}
          onClick={() => onToggleSave(listing)}
          title={isSaved ? 'Убрать из сохранённых' : 'Сохранить'}
        >
          <Bookmark className="w-4 h-4" fill={isSaved ? 'currentColor' : 'none'} />
        </button>
      )}
      {matchScore != null && (
        <div className="absolute top-2 right-2 z-10">
          <div className="radial-progress bg-base-100 text-primary border-2 border-base-100 text-xs" style={{ '--value': matchScore, '--size': '3rem' }}>
            {Math.round(matchScore)}%
          </div>
        </div>
      )}
      {listing.cover_image_url ? (
        <figure className="h-40 overflow-hidden">
          <img
            src={listing.cover_image_url}
            alt={listing.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </figure>
      ) : (
        <div className="bg-gradient-to-r from-primary/20 to-accent/20 h-32 flex items-center justify-center text-5xl">
          🌍
        </div>
      )}

      <div className="card-body">
        <div className="badge badge-secondary badge-outline">{listing.listing_type_display}</div>
        <h2 className="card-title text-lg">{listing.title}</h2>
        {listing.description && (
          <p className="text-gray-600 text-sm line-clamp-3">{listing.description}</p>
        )}

        {reason && (
          <p className="text-sm text-primary flex items-start gap-1 mt-1">
            <Sparkles className="w-4 h-4 shrink-0 mt-0.5" />
            {reason}
          </p>
        )}

        <div className="space-y-2 my-4 text-sm">
          {listing.organization_name && (
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-primary" />
              <span>{listing.organization_name}</span>
            </div>
          )}
          {listing.is_online ? (
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-primary" />
              <span>Онлайн</span>
            </div>
          ) : listing.region ? (
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-primary" />
              <span>{listing.region}</span>
            </div>
          ) : null}
          {startDate && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-primary" />
              <span>{startDate}</span>
            </div>
          )}
          {deadline && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-error" />
              <span>Дедлайн: {deadline}</span>
            </div>
          )}
        </div>

        {listing.tags?.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {listing.tags.map((tag) => (
              <span key={tag.id} className="badge badge-ghost badge-sm">
                {tag.name}
              </span>
            ))}
          </div>
        )}

        <div className="card-actions justify-between items-center pt-2">
          {listing.source_name && (
            <span className="text-xs text-gray-400 truncate max-w-[40%]">{listing.source_name}</span>
          )}
          {listing.source_url && (
            <a
              href={listing.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary btn-sm gap-1 ml-auto"
            >
              Перейти к источнику
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

export default ListingCard;
